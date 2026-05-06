# Aula 09 — "Explicar com IA": integrando uma LLM gratuita

## Objetivo

Botão **"Explicar com IA"** no detalhe do post. Ao clicar, chamamos uma LLM (modelo de linguagem) gratuita, que devolve uma explicação aprofundada sobre o tópico do post. O texto é guardado num novo campo `ai_explanation` e exibido logo abaixo da descrição.

```
[ usuário clica botão ]──► view ──► services.gerar_explicacao_ia(post)
                                              │
                                              ▼
                                       [ Groq API (LLM) ]
                                              │
                                              ▼
                              post.ai_explanation = texto
                              post.save() ──► redirect detail
```

> **Onde mora a regra?** Pela hierarquia da [Aula 06](aula-06-regras-de-negocio.md): chamar uma API externa é **efeito colateral** → vai em `posts/services.py`. A view só orquestra.

---

## 1. Por que Groq?

Existem várias LLMs gratuitas para usar via API. Comparativo rápido:

| Provedor | Custo | Cadastro | Velocidade | Modelo padrão |
|---|---|---|---|---|
| **Groq** ✅ | Grátis (sem cartão) | Email | Muito rápida (~1s) | Llama 3.1 / 3.3 |
| Google Gemini | Grátis (15 RPM) | Conta Google | Média | Gemini 1.5 Flash |
| Hugging Face | Grátis (limitado) | Email | Lenta | Vários |
| Ollama | Grátis (local) | Nada | Depende da máquina | Você baixa |

Vamos usar a **Groq** porque:

- **Não pede cartão de crédito** — ideal para sala de aula.
- **API muito rápida** (a Groq usa hardware próprio, LPU, otimizado para inference).
- **SDK em Python** (`pip install groq`) com sintaxe quase idêntica à da OpenAI.
- **Free tier generoso** para uso didático: 30 requisições/minuto, 14.400 por dia.

---

## 2. Pegar a API key

1. Acesse <https://console.groq.com/keys>.
2. Faça cadastro com email/Google/GitHub.
3. Clique em **Create API Key**, dê um nome (ex: `posts-trilha`) e copie a chave (começa com `gsk_...`).
4. **Guarde**: a chave só aparece uma vez. Se perder, gera outra.

> **Aviso de segurança:** essa chave é como uma senha. **Nunca** comite no Git, nunca poste em screenshot, nunca exponha em frontend.

---

## 3. Configurar o `.env`

Adicione a chave ao seu `app/.env` (criado na Aula 02):

```env
SECRET_KEY=...
DEBUG=True
DB_NAME=...
# ... (linhas anteriores) ...

GROQ_API_KEY=gsk_sua_chave_aqui
```

Em `config/settings.py`, leia a variável:

```python
GROQ_API_KEY = config('GROQ_API_KEY')
```

> Como o `.env` já está no `.gitignore` desde a Aula 01, a chave não vai parar no repositório.

---

## 4. Instalar o SDK

```bash
pip install groq
```

Verifique:

```bash
python -c "from groq import Groq; print('ok')"
```

---

## 5. Adicionar o campo `ai_explanation` ao Post

Em `posts/models.py`:

```python
class Post(models.Model):
    # ... campos anteriores ...
    descricao = models.TextField()
    ai_explanation = models.TextField(blank=True, default='')
    status = models.CharField(...)
    # ... resto igual ...
```

| Detalhe | Por quê |
|---|---|
| `TextField` | Tamanho indefinido — uma resposta de LLM pode passar de 500 caracteres facilmente |
| `blank=True` | Form aceita sem preencher (vai começar vazio em todo post) |
| `default=''` | No banco, valor inicial é string vazia (não `NULL`) — evita ter que checar `if post.ai_explanation is not None` no template |

Migrar:

```bash
python manage.py makemigrations posts
python manage.py migrate
```

Como definimos `default=''`, o Django aplica o default sem precisar perguntar nada.

---

## 6. Service: a função que chama a LLM

`posts/services.py` — adicione após `gerar_pdf_do_post`:

```python
from django.conf import settings
from groq import Groq


def gerar_explicacao_ia(post) -> str:
    """Chama a LLM da Groq para explicar o tópico do post de forma aprofundada."""
    client = Groq(api_key=settings.GROQ_API_KEY)

    prompt = (
        "Você é um educador que explica conceitos de forma clara, didática "
        "e aprofundada em português brasileiro. Use exemplos quando útil.\n\n"
        f"Tópico: {post.titulo}\n\n"
        f"Contexto adicional (escrito pelo autor):\n{post.descricao}\n\n"
        "Escreva uma explicação aprofundada do tópico em até 6 parágrafos."
    )

    resposta = client.chat.completions.create(
        model='llama-3.1-8b-instant',
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=1000,
        temperature=0.7,
    )

    return resposta.choices[0].message.content.strip()
```

| Detalhe | Por quê |
|---|---|
| Função, não classe | Sem estado a guardar (mesma decisão da Aula 06) |
| Recebe `post`, devolve `str` | Não toca no banco; só **gera** texto. Quem persiste é a view |
| `settings.GROQ_API_KEY` | Lê da config (que veio do `.env`). Nunca hardcode chaves |
| `model='llama-3.1-8b-instant'` | Modelo pequeno e rápido. Para respostas mais longas/elaboradas, `llama-3.3-70b-versatile` |
| `max_tokens=1000` | Teto de tamanho. ~750 palavras. Protege contra resposta gigante e custo (no free tier, isso é cota) |
| `temperature=0.7` | Quão "criativo" o modelo é. 0 = determinístico, 1 = bem variado. 0.7 é bom para explicações |
| `.strip()` | Remove espaços/quebras nas pontas — resposta de LLM costuma vir com `\n\n` no fim |

> **Por que o service NÃO salva no banco?** Para ser reaproveitável. Imagine amanhã uma `management command` que pré-gera explicações em massa, ou um endpoint que devolve a explicação como JSON sem persistir. Mantendo `gerar_explicacao_ia` como "transformador puro" (post in, texto out), tudo isso fica trivial.

---

## 7. View: orquestração thin

`posts/views.py` — adicione no fim:

```python
from .services import gerar_explicacao_ia, gerar_pdf_do_post


@require_POST
def post_explicar(request, pk):
    post = get_object_or_404(Post, pk=pk, autor=request.user)
    post.ai_explanation = gerar_explicacao_ia(post)
    post.save(update_fields=['ai_explanation'])
    return redirect('posts:detail', pk=pk)
```

| Linha | Função |
|---|---|
| `@require_POST` | Geração custa tempo e cota — proibimos GET para evitar disparo acidental por crawler/preload |
| `get_object_or_404(..., autor=request.user)` | Mesma proteção das aulas anteriores: post de outro usuário não existe |
| `gerar_explicacao_ia(post)` | Service faz o trabalho pesado. View nem importa o `Groq` |
| `update_fields=['ai_explanation']` | Salva só a coluna nova — não sobrescreve campos modificados em paralelo |

---

## 8. URL

`posts/urls.py`:

```python
urlpatterns = [
    path('', views.PostListView.as_view(), name='list'),
    path('novo/', views.PostCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.PostUpdateView.as_view(), name='update'),
    path('<int:pk>/excluir/', views.PostDeleteView.as_view(), name='delete'),
    path('<int:pk>/finalizar/', views.post_finalizar, name='finalizar'),
    path('<int:pk>/pdf/', views.post_pdf, name='pdf'),
    path('<int:pk>/explicar-ia/', views.post_explicar, name='explicar_ia'),
]
```

---

## 9. Botão e exibição no detalhe

`posts/templates/posts/detail.html` — adicione **dentro do `<article>`**, após a `descricao`:

```html
<div class="descricao mb-6">{{ post.descricao }}</div>

{% if post.ai_explanation %}
    <section class="bg-purple-50 border border-purple-200 p-4 rounded mb-6">
        <h3 class="font-bold text-purple-900 mb-2 flex items-center gap-2">
            <span>🤖</span> Explicação detalhada (IA)
        </h3>
        <div class="prose whitespace-pre-line text-gray-800">{{ post.ai_explanation }}</div>
    </section>
{% endif %}
```

E no bloco de botões de ação, adicione:

```html
<form method="post" action="{% url 'posts:explicar_ia' post.pk %}" class="inline">
    {% csrf_token %}
    <button type="submit" class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">
        {% if post.ai_explanation %}🔄 Regerar explicação{% else %}🤖 Explicar com IA{% endif %}
    </button>
</form>
```

| Decisão | Por quê |
|---|---|
| Botão muda de label se já há explicação | Comunica claramente que vai **substituir** a anterior |
| `<form method="post">` com CSRF | Operação que muda estado **sempre** em POST. Igual ao botão "Finalizar" da Aula 06 |
| Cor roxa | Diferencia visualmente das outras ações (azul = navegação, amarelo = editar, vermelho = excluir) |

---

## 10. Tratar erros

A chamada à API pode falhar — sem internet, chave inválida, rate limit. Vamos cobrir o caso.

`posts/views.py`:

```python
from django.contrib import messages
from groq import GroqError


@require_POST
def post_explicar(request, pk):
    post = get_object_or_404(Post, pk=pk, autor=request.user)
    try:
        post.ai_explanation = gerar_explicacao_ia(post)
        post.save(update_fields=['ai_explanation'])
        messages.success(request, 'Explicação gerada com sucesso.')
    except GroqError as e:
        messages.error(request, f'Não foi possível gerar a explicação: {e}')
    return redirect('posts:detail', pk=pk)
```

E para mostrar a mensagem, adicione no `templates/base.html`, dentro do `<main>` antes do `{% block content %}`:

```html
{% if messages %}
    <div class="mb-4 space-y-2">
        {% for message in messages %}
            <div class="p-3 rounded {% if message.tags == 'error' %}bg-red-100 text-red-800{% else %}bg-green-100 text-green-800{% endif %}">
                {{ message }}
            </div>
        {% endfor %}
    </div>
{% endif %}
```

> **Framework de mensagens?** O `django.contrib.messages` já vem habilitado por padrão em `INSTALLED_APPS` e `MIDDLEWARE`. Você só precisa exibir.

---

## 11. Testar

```bash
python manage.py runserver
```

1. Logado, abra um post com título + descrição preenchidos.
2. Clique em **🤖 Explicar com IA**. A página recarrega após ~1-2s com a explicação na seção roxa.
3. Clique em **🔄 Regerar explicação**. O texto muda (a LLM é probabilística — `temperature=0.7` garante variação).
4. Tente como **outro usuário** acessar `/posts/<id>/explicar-ia/` (POST) → 404. ✅
5. Como teste de erro: temporariamente troque `GROQ_API_KEY` no `.env` por algo inválido. Reinicie o servidor, clique no botão. Deve aparecer a mensagem vermelha de erro.
6. **Restaure** a chave correta antes de continuar.

---

## 12. Custos e limites

| Limite | Valor (free tier Groq, abr/2026) |
|---|---|
| Requisições por minuto | 30 |
| Requisições por dia | 14.400 |
| Tokens por minuto | 6.000 |
| Tokens por dia | 500.000 |

Para a sala de aula é mais que suficiente. Se em algum momento você passar do limite, a API devolve **429 Too Many Requests** — o `try/except` que adicionamos captura como `GroqError` e mostra ao usuário.

---

## 13. Para onde ir a partir daqui

A versão da aula é deliberadamente **síncrona**: o usuário clica e espera. Funciona para 1-2 segundos da Llama 3.1. Para evolução real:

- **Async com `Celery`** — gerar em background, polling/Websocket para mostrar quando terminar.
- **Streaming de tokens** — ver a resposta surgindo palavra por palavra (a Groq suporta com `stream=True` e SSE no front).
- **HTMX** — substituir o reload da página por uma swap parcial: clica → spinner → texto aparece sem reload.
- **Histórico de explicações** — em vez de um campo só, criar um model `ExplicacaoIA(post=FK, texto, criada_em)`.
- **Trocar de provedor** — abstrair o service para aceitar Groq, Gemini ou Ollama via configuração. Hoje nosso `gerar_explicacao_ia` está acoplado à Groq; a porta para isso é uma camada `posts/services/llm.py` com `def chamar_llm(prompt) -> str` que esconde o cliente.

---

## Exercício

1. Cadastre-se na Groq e pegue a API key.
2. Adicione `GROQ_API_KEY` ao `.env` e leia em `settings.py`.
3. Instale a lib (`pip install groq`).
4. Adicione o campo `ai_explanation` ao Post e migre.
5. Crie a função `gerar_explicacao_ia(post)` em `posts/services.py`.
6. Crie a view `post_explicar` (com `@require_POST`).
7. Adicione a rota `posts/<id>/explicar-ia/`.
8. Coloque botão e exibição no `detail.html`.
9. Mostre `messages` no `base.html` para feedback.
10. Faça os 6 testes da seção 11.
11. (Opcional) Edite o prompt — peça a explicação em formato de bullets, ou em tom de "eu tenho 5 anos". Compare resultados.
12. (Opcional) Troque `llama-3.1-8b-instant` por `llama-3.3-70b-versatile` e veja a diferença de qualidade vs latência.

---

## 🔁 Vindo do Rails

| Conceito | Rails | Django |
|---|---|---|
| Cliente OpenAI-compatible | gem `openai` ou `ruby-openai` (configura via `OpenAI::Client.new`) | SDK próprio: `groq`, `openai`, `anthropic`, `google-genai` |
| API key em config | `Rails.application.credentials.groq[:api_key]` (criptografado) ou `dotenv-rails` | `python-decouple` lendo `.env` |
| Acesso à config | `Rails.application.credentials.groq[:api_key]` em qualquer lugar | `from django.conf import settings; settings.GROQ_API_KEY` |
| Service object | `app/services/gerar_explicacao_ia.rb` (PORO `.call(post)`) | `posts/services.py` com função `gerar_explicacao_ia(post)` |
| Rota só POST | `post '/posts/:id/explicar_ia', to: 'posts#explicar_ia'` | `path('<int:pk>/explicar-ia/', views.post_explicar, name='explicar_ia')` + `@require_POST` |
| Flash messages | `flash[:success] = '...'` no controller; `<%= flash[:success] %>` no view | `messages.success(request, '...')`; loop `{% for message in messages %}` no template |
| Salvar coluna específica | `post.update_columns(ai_explanation: texto)` (sem callbacks) | `post.ai_explanation = texto; post.save(update_fields=['ai_explanation'])` |
| Background job para LLM lenta | Active Job + Sidekiq (`ExplicarPostJob.perform_later(post)`) | Celery (`explicar_post_task.delay(post_id)`) |
| Streaming de tokens (futuro) | Action Cable / Turbo Streams | Channels / HTMX SSE |

> 💎 **`messages` ≈ `flash`.** O framework de mensagens do Django funciona quase igual ao `flash` do Rails: você empurra mensagens no controller/view (`messages.success`, `.error`, `.info`, `.warning`), elas vivem na sessão até serem renderizadas, e somem depois. A diferença é que no Django você **escolhe quando renderizar** com um `{% for message in messages %}` — não tem helper "automático" que aparece no layout.

> 💎 **`update_fields=['x']` ≈ `update_columns(x: ...)`, mas com signals.** Como vimos na Aula 06: ambos pulam *callbacks pesados*, mas `save(update_fields=...)` no Django **continua disparando o signal `post_save`** (com a lista do que mudou). Em Rails, `update_columns` pula tudo. Útil saber se você tem listeners no `post_save`.

> 💎 **Não há `Rails.application.credentials` criptografado por padrão.** A solução nativa do Django é o `.env` (texto puro, fora do Git via `.gitignore`). Para produção séria, equivalentes ao credentials seriam: AWS Secrets Manager, HashiCorp Vault, ou uma lib como `django-environ` apontando para um secret manager. A trilha usa `.env` simples — basta para sala de aula.

> 💎 **SDK próprio por provedor.** Em Rails, é comum uma única `ruby-openai` cobrir múltiplos providers via base URL. Em Python, cada provedor publica seu próprio SDK (`groq`, `openai`, `anthropic`, `google-genai`). A Groq, especificamente, também é compatível com o SDK da OpenAI — você poderia usar `from openai import OpenAI` e apontar `base_url='https://api.groq.com/openai/v1'`. Como a lib `groq` já é nativa, usamos ela direto.

---

🎉 **Fim atualizado da trilha.** Seu sistema agora tem: autenticação, controle de acesso, regras de negócio organizadas, upload de imagem, geração de PDF e **explicação automática via LLM**. A última aula é também o melhor exemplo da hierarquia da Aula 06: service isolado, view thin, model só com o campo novo.
