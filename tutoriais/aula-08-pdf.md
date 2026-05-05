# Aula 08 — Geração de PDF do post

## Objetivo

Botão **"Baixar PDF"** na página de detalhe. Ao clicar, o usuário recebe um arquivo `.pdf` contendo o **título**, a **imagem** (se houver) e a **descrição** do post.

```
[ /posts/<id>/pdf/ ] ──► view ──► render(template) ──► HTML ──► WeasyPrint ──► PDF ──► download
```

A estratégia: **renderizar um template HTML** (igual a uma página comum) e converter esse HTML em PDF com a biblioteca **WeasyPrint**. Vantagem: você desenha o PDF com HTML e CSS, não com chamadas imperativas estilo `pdf.draw_text(x, y, ...)`.

> **Onde mora a regra?** Pela hierarquia da [Aula 06](aula-06-regras-de-negocio.md), gerar PDF tem **efeito colateral** (renderiza arquivo) e usa **biblioteca externa** (WeasyPrint). Lugar certo: **`posts/services.py`**. A view só orquestra: pega o post, chama o service, devolve a resposta HTTP.

---

## 1. Instalar WeasyPrint

```bash
pip install weasyprint
```

WeasyPrint depende de bibliotecas de sistema para fontes e renderização. **Faça a instalação do SO antes**, se ainda não tem:

### macOS

```bash
brew install pango
```

### Linux (Debian/Ubuntu)

```bash
sudo apt install libpango-1.0-0 libpangoft2-1.0-0
```

### Windows

Siga o guia oficial: <https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows>. Tipicamente envolve instalar o **GTK runtime**.

> **Por que WeasyPrint e não ReportLab?** ReportLab te obriga a posicionar tudo manualmente (`canvas.drawString(50, 800, "título")`). WeasyPrint aceita HTML+CSS — você reaproveita o que já sabe da web.

Verifique:

```bash
python -c "from weasyprint import HTML; print('ok')"
```

---

## 2. Template do PDF

PDFs renderizam melhor com um template **separado** do HTML do navegador (sem navbar, sem JavaScript, com CSS impresso embutido).

`posts/templates/posts/pdf.html`:

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>{{ post.titulo }}</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'Helvetica', sans-serif;
            color: #222;
            line-height: 1.5;
        }
        h1 {
            font-size: 24pt;
            margin-bottom: 4pt;
            color: #1d4ed8;
        }
        .meta {
            font-size: 10pt;
            color: #6b7280;
            margin-bottom: 16pt;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 8pt;
        }
        .imagem {
            text-align: center;
            margin: 16pt 0;
        }
        .imagem img {
            max-width: 100%;
            max-height: 10cm;
        }
        .descricao {
            font-size: 11pt;
            white-space: pre-line;
        }
        footer {
            position: fixed;
            bottom: -1cm;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 9pt;
            color: #9ca3af;
        }
    </style>
</head>
<body>
    <h1>{{ post.titulo }}</h1>
    <div class="meta">
        Status: {{ post.get_status_display }} ·
        Criado em {{ post.criado_em|date:"d/m/Y H:i" }} ·
        Autor: {{ post.autor.username }}
    </div>

    {% if post.imagem %}
        <div class="imagem">
            <img src="{{ imagem_absoluta }}" alt="">
        </div>
    {% endif %}

    <div class="descricao">{{ post.descricao }}</div>

    <footer>Gerado em {{ gerado_em|date:"d/m/Y H:i" }}</footer>
</body>
</html>
```

| Detalhe | Função |
|---|---|
| `@page { size: A4; margin: 2cm }` | CSS específico de impressão — define o tamanho da folha |
| `imagem_absoluta` | Caminho absoluto da imagem no disco — explicado no próximo passo |
| `position: fixed` no footer | Aparece em todas as páginas, não só na primeira |

---

## 3. Por que `imagem_absoluta`?

WeasyPrint **não é um navegador**: ele não faz requisição HTTP para `/media/posts/foto.jpg`. Ele lê o arquivo direto do disco. Então em vez de passar `post.imagem.url` (`/media/posts/foto.jpg`), passamos `post.imagem.path` (caminho absoluto no sistema, tipo `/Users/.../app/media/posts/foto.jpg`).

---

## 4. Service: a função que gera o PDF

Toda a interação com WeasyPrint (template + bytes) vai morar aqui. Abra o `posts/services.py` que você criou na [Aula 06](aula-06-regras-de-negocio.md) e adicione:

```python
"""Funções que orquestram regras de negócio do app posts."""

from django.template.loader import render_to_string
from django.utils import timezone

from weasyprint import HTML


def gerar_pdf_do_post(post) -> bytes:
    html_string = render_to_string('posts/pdf.html', {
        'post': post,
        'imagem_absoluta': post.imagem.path if post.imagem else None,
        'gerado_em': timezone.now(),
    })
    return HTML(string=html_string).write_pdf()
```

| Detalhe | Por quê |
|---|---|
| Função, não classe | Sem estado a guardar — função é mais simples |
| Recebe `post`, devolve `bytes` | Dependência clara: precisa só do post; não precisa de `request` nem de `user` |
| Type hint `-> bytes` | Documenta o retorno. Quem chama sabe o que esperar sem precisar ler o corpo |

**Repare no que ficou de fora**: nada de `HttpResponse`, nada de validação de dono, nada de URL. Esses são assuntos de view — o service só sabe transformar `Post` em PDF.

## 5. View — só orquestração

`posts/views.py` — adicione no fim:

```python
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .services import gerar_pdf_do_post


def post_pdf(request, pk):
    post = get_object_or_404(Post, pk=pk, autor=request.user)
    pdf_bytes = gerar_pdf_do_post(post)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="post-{post.pk}.pdf"'
    return response
```

Cinco linhas. Cada uma faz uma coisa de view: validar dono via 404, chamar o domínio, montar a resposta.

| Linha | Função |
|---|---|
| `get_object_or_404(Post, pk=pk, autor=request.user)` | Busca **e** valida dono numa só query. Se outro usuário tentar baixar, recebe 404 |
| `gerar_pdf_do_post(post)` | Delega para o service. A view não sabe o que é WeasyPrint nem precisa importar `render_to_string` |
| `Content-Disposition: attachment; filename=...` | Diz ao navegador "baixe esse arquivo, não exiba" e sugere um nome |

> **Decorator `@login_required`?** Não precisa: o `get_object_or_404` exige `autor=request.user`, e se o usuário estiver deslogado `request.user` é o `AnonymousUser` — a query nunca casa, dá 404. Se quiser ser explícito (e dar redirect para login em vez de 404), adicione `@login_required` no topo da função.

> **Por que separar?** Amanhã, se quiser mandar o PDF por email (`enviar_post_por_email(user, post)`), reaproveita `gerar_pdf_do_post(post)` direto, sem passar por view nenhuma.

---

## 6. URL

`posts/urls.py` — adicione mais uma linha (junto com `finalizar` da Aula 06):

```python
urlpatterns = [
    path('', views.PostListView.as_view(), name='list'),
    path('novo/', views.PostCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.PostUpdateView.as_view(), name='update'),
    path('<int:pk>/excluir/', views.PostDeleteView.as_view(), name='delete'),
    path('<int:pk>/finalizar/', views.post_finalizar, name='finalizar'),
    path('<int:pk>/pdf/', views.post_pdf, name='pdf'),
]
```

---

## 7. Botão de download no detalhe

`posts/templates/posts/detail.html`, dentro dos botões de ação:

```html
<div class="flex gap-3">
    <a href="{% url 'posts:update' post.pk %}" class="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600">Editar</a>
    <a href="{% url 'posts:delete' post.pk %}" class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Excluir</a>
    <a href="{% url 'posts:pdf' post.pk %}" class="bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-800">
        Baixar PDF
    </a>
    <a href="{% url 'posts:list' %}" class="text-gray-600 hover:underline self-center ml-auto">Voltar</a>
</div>
```

---

## 8. Testar

```bash
python manage.py runserver
```

1. Logado, abra um post (com imagem).
2. Clique em **Baixar PDF** → o navegador deve baixar `post-1.pdf`.
3. Abra o PDF: título, status, autor, imagem e descrição devem aparecer.
4. Repita com um post **sem** imagem → o PDF sai sem o bloco da imagem.
5. Faça logout e tente acessar `/posts/1/pdf/` direto na URL → 404 (ou redirect para login, se você usou `@login_required`).
6. Logado como **outro** usuário, tente `/posts/1/pdf/` → 404. ✅

---

## 9. Erros comuns e como resolver

| Sintoma | Causa provável | Conserto |
|---|---|---|
| `OSError: cannot load library 'libpango...'` | Falta instalar Pango no SO | Volte ao passo 1 |
| Imagem não aparece no PDF | Passou `post.imagem.url` em vez de `.path` | Conferir contexto da view |
| PDF abre como página HTML no navegador | Falta `Content-Disposition` ou `content_type` | Conferir headers da response |
| Acentuação quebrada | Falta `<meta charset="UTF-8">` no template do PDF | Adicionar no `<head>` |

---

## Para onde ir a partir daqui

- **Cache do PDF** — gerar PDF é caro. Se um post não muda, dá pra cachear o resultado por `pk + updated_at`.
- **Job em background** — para PDFs gigantes, usar Celery para gerar fora do request.
- **Salvar como `FileField`** — em vez de devolver direto, gravar o PDF no disco e oferecer link permanente.
- **Outras saídas** — a mesma view pode virar `?formato=html` para preview e `?formato=pdf` para download.

---

## Exercício

1. Instale WeasyPrint (e as deps do SO).
2. Crie `posts/templates/posts/pdf.html` com `@page` e estilos próprios para impressão.
3. Crie a função `gerar_pdf_do_post(post)` em `posts/services.py` (o arquivo que você preparou na Aula 06).
4. Crie a view `post_pdf` filtrando por `autor=request.user` e delegando para o service.
5. Adicione a rota `posts/<id>/pdf/`.
6. Coloque o botão "Baixar PDF" no detalhe.
7. Teste com post com imagem, sem imagem e como outro usuário (deve dar 404).
8. (Opcional) Adicione número da página no rodapé com `@page { @bottom-right { content: "Página " counter(page); } }`.
9. (Opcional) No `shell`, gere o PDF sem passar pela view: `from posts.services import gerar_pdf_do_post; from posts.models import Post; open('teste.pdf', 'wb').write(gerar_pdf_do_post(Post.objects.first()))`. Esse "reaproveitamento fora do request" é exatamente o motivo do service existir.

---

## 🔁 Vindo do Rails

| Conceito | Rails | Django |
|---|---|---|
| Lib HTML→PDF mais comum | `wicked_pdf` (wkhtmltopdf), `grover` (Puppeteer), `prawn` (imperativo) | **WeasyPrint** (HTML+CSS), `xhtml2pdf`, `reportlab` (imperativo) |
| Onde mora a lógica | `app/services/gerar_pdf_do_post.rb` (PORO com `.call`) | `posts/services.py` com função |
| Renderizar template para string | `render_to_string('posts/pdf', layout: false, locals: {post: post})` | `render_to_string('posts/pdf.html', {'post': post})` |
| Devolver PDF como download | `send_data pdf_bytes, type: 'application/pdf', disposition: 'attachment', filename: 'foo.pdf'` | `HttpResponse(pdf_bytes, content_type='application/pdf')` + header `Content-Disposition` |
| Caminho de imagem no template do PDF | `image_tag rails_blob_path(post.imagem, only_path: true)` (URL) — wkhtmltopdf precisa de URL pública | `<img src="{{ post.imagem.path }}">` (caminho de disco) — WeasyPrint lê do filesystem |
| Background job para PDF pesado | Active Job + Sidekiq (`PostPdfJob.perform_later(post)`) | `Celery` ou `dramatiq` ou `django-q` |
| Cache de PDF gerado | `Rails.cache.fetch("post-#{id}-pdf-#{updated_at.to_i}") { ... }` | `from django.core.cache import cache; cache.get_or_set('post-pdf-...', lambda: ..., 3600)` |

> 💎 **`render_to_string` tem o mesmo nome nos dois.** Um dos pouquíssimos casos de paridade direta. A diferença está apenas em como você passa as variáveis: Rails usa `locals: {...}`, Django passa um dict no segundo argumento.

> 💎 **`send_data` ↔ `HttpResponse` + headers.** Rails encapsula download num único helper (`send_data` ou `send_file`). Django é mais cru: você monta um `HttpResponse` com `content_type` e seta `Content-Disposition` na mão. Mais boilerplate, mas você tem visibilidade total dos headers — útil para depurar.

> 💎 **WeasyPrint lê do disco; wkhtmltopdf lê via HTTP.** É a diferença mais armadilhosa quando você migra entre stacks. No Rails com `wicked_pdf`/wkhtmltopdf, você passa **URLs** das imagens (`asset_path`, `rails_blob_url`). No Django com WeasyPrint, você passa **paths absolutos** (`post.imagem.path`). Trocar um pelo outro causa "imagem não aparece no PDF" silencioso.

> 💎 **Service como função reaproveitável fora do request.** Em Rails, o paralelo é o `app/services/` que você chama tanto do controller quanto de um job ou rake task. O exercício final desta aula (gerar PDF no shell sem passar pela view) é exatamente isso: a mesma `gerar_pdf_do_post(post)` serve para o request HTTP, para um `management command` (`python manage.py exportar_pdfs`) e para um job Celery.

---

🎉 **Fim da trilha.** Você saiu de zero (Aula 01) até um sistema multiusuário com autenticação, controle de acesso, upload de arquivos e geração de PDF.
