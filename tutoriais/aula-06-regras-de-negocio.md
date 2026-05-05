# Aula 06 — Regras de negócio: onde colocar?

## Objetivo

Toda vez que aparece um requisito novo ("marque o post como finalizado", "filtre só os em progresso", "gere um PDF") surge a mesma dúvida: **onde mora esse código?** Na view? No model? Numa classe nova?

Esta aula apresenta a **hierarquia pragmática** que a comunidade Django usa, e aplica de imediato no nosso projeto.

```
┌──────────────────────────────────────────────────────────────┐
│  É sobre UMA instância?              → método no model       │
│  É sobre CONSULTA de várias?         → Manager/QuerySet      │
│  Tem efeito colateral (email, PDF)?  → services.py           │
│  Apenas request/response?            → view                  │
└──────────────────────────────────────────────────────────────┘
```

> **Princípio:** comece no lugar mais simples. **Promova** para o próximo nível só quando doer.

---

## 1. Os quatro lugares (do mais simples ao mais elaborado)

### 1.1 No model — para regras sobre uma instância

Tudo que diz respeito a **um único registro** — validação, cálculo derivado, mudança de estado — vive no model.

Sintomas: a regra começa com "este post...". Exemplos: `post.finalizar()`, `post.dias_em_aberto`, `post.pode_ser_excluido()`.

**Por quê?** O Django chama isso de **fat model**. A instância já tem todos os dados necessários — pedir a uma view ou service para mexer nela seria criar uma volta desnecessária.

### 1.2 Manager / QuerySet — para consultas de muitos

Tudo que filtra, agrupa, ordena ou conta vários registros. Em vez de espalhar `.filter(status=...)` pela view, dá um nome ao filtro e o coloca no QuerySet.

Sintomas: a regra começa com "todos os posts que...". Exemplos: `Post.objects.do_usuario(user)`, `Post.objects.em_progresso()`, `Post.objects.criados_esta_semana()`.

**Por quê?** Faz a consulta virar **vocabulário do domínio**. Sua view passa a ler `Post.objects.do_usuario(user).em_progresso()` em vez de `Post.objects.filter(autor=user, status='em_progresso')`.

### 1.3 services.py — para orquestração e efeitos colaterais

Quando a regra:
- envolve **mais de um model**,
- tem **efeito colateral** (manda email, escreve arquivo, chama API externa, dispara job),
- ou é grande/complexa demais para caber natural num model.

Você cria um arquivo `services.py` no app e coloca **funções**.

Sintomas: a regra começa com um verbo de ação ampla — "gerar", "enviar", "processar", "importar", "sincronizar". Exemplos: `gerar_pdf_do_post(post)`, `enviar_resumo_semanal(usuario)`, `importar_posts_do_csv(arquivo)`.

**Por quê?** O model não deve saber sobre PDFs nem emails — isso o acoplaria a bibliotecas externas. Uma função em `services.py` orquestra: pega dados do model, chama a biblioteca, devolve o resultado.

> **Função ou classe?** Comece com **função**. Classe só se houver estado a guardar entre chamadas (raro).

### 1.4 View — apenas request/response

A view tem **um trabalho**: traduzir HTTP em chamadas para o domínio e devolver uma resposta.

Sintomas: usa `request`, devolve `HttpResponse`/`render`/`redirect`. Não tem `if status == ...`, não tem `for` somando coisas, não tem `email.send()` direto.

```python
# Bom — fina, delega para o domínio:
def post_finalizar(request, pk):
    post = get_object_or_404(Post, pk=pk, autor=request.user)
    post.finalizar()
    return redirect('posts:detail', pk=pk)
```

```python
# Ruim — view que carrega regra:
def post_finalizar(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.autor != request.user:
        return HttpResponseForbidden()
    post.status = 'finalizado'
    post.atualizado_em = timezone.now()
    post.save()
    enviar_email_de_conclusao(post)
    return redirect(...)
```

---

## 2. Aplicando no nosso projeto

Vamos refatorar três pontos do que já existe — cada um exemplifica um dos lugares.

### 2.1 Refator A — método no model: `finalizar()` e `esta_finalizado`

Hoje, no template, comparamos string crua:

```html
{% if post.status == 'finalizado' %}bg-green-100{% else %}bg-yellow-100{% endif %}
```

Isso acopla o template ao **valor literal** do enum. Se um dia mudarmos o valor para `'concluido'`, quebra silenciosamente. Vamos esconder atrás de uma propriedade.

`posts/models.py`:

```python
class Post(models.Model):
    class Status(models.TextChoices):
        EM_PROGRESSO = 'em_progresso', 'Em progresso'
        FINALIZADO = 'finalizado', 'Finalizado'

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    titulo = models.CharField(max_length=120)
    descricao = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.EM_PROGRESSO,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo

    # ───── Regras sobre UMA instância ─────

    @property
    def esta_finalizado(self):
        return self.status == self.Status.FINALIZADO

    def finalizar(self):
        self.status = self.Status.FINALIZADO
        self.save(update_fields=['status'])
```

| Detalhe | Por quê |
|---|---|
| `@property` em `esta_finalizado` | No template vira `{% if post.esta_finalizado %}` — sem parênteses, leitura natural |
| `self.Status.FINALIZADO` (não `'finalizado'`) | Compara com a constante, não com a string. Se o valor mudar, basta editar o `TextChoices` |
| `update_fields=['status']` | `save()` só escreve a coluna `status`. Mais rápido e evita sobrescrever campos modificados em paralelo |

Ajuste o template `posts/templates/posts/list.html`:

```html
<span class="ml-2 text-xs px-2 py-1 rounded
    {% if post.esta_finalizado %}bg-green-100 text-green-800{% else %}bg-yellow-100 text-yellow-800{% endif %}">
    {{ post.get_status_display }}
</span>
```

Mais legível, e **uma única fonte da verdade** para a definição de "finalizado".

### 2.2 Refator B — QuerySet: `do_usuario()` e `em_progresso()`

Hoje o mixin de controle de acesso filtra inline:

```python
class OwnedQuerysetMixin:
    def get_queryset(self):
        return super().get_queryset().filter(autor=self.request.user)
```

Vamos dar nome a esse filtro no nível certo (QuerySet), porque ele descreve o **domínio**: "posts do usuário".

`posts/models.py` — adicione antes da classe `Post`:

```python
from django.db import models


class PostQuerySet(models.QuerySet):
    def do_usuario(self, user):
        return self.filter(autor=user)

    def em_progresso(self):
        return self.filter(status=Post.Status.EM_PROGRESSO)

    def finalizados(self):
        return self.filter(status=Post.Status.FINALIZADO)
```

E na classe `Post`, registre o queryset como manager:

```python
class Post(models.Model):
    # ... Status, campos, Meta, métodos como antes ...

    objects = PostQuerySet.as_manager()
```

Agora atualize `posts/views.py` — o mixin fica mais limpo:

```python
class OwnedQuerysetMixin:
    def get_queryset(self):
        return super().get_queryset().do_usuario(self.request.user)
```

E em qualquer outro lugar que precisar contar/listar:

```python
Post.objects.do_usuario(request.user).em_progresso().count()
```

> **Por que `as_manager()` em vez de declarar uma classe `PostManager`?** Para não duplicar. O método precisa estar disponível tanto em `Post.objects.do_usuario(u)` quanto em `outro_queryset.do_usuario(u)` — `as_manager()` faz isso por você.

### 2.3 Refator C — services.py: vamos preparar o terreno

Crie o arquivo agora, vazio com um docstring. A próxima aula (PDF) vai colocar a primeira função aqui.

`posts/services.py`:

```python
"""Funções que orquestram regras de negócio do app posts.

Coloque aqui código que:
- envolve mais de um model,
- tem efeito colateral (gerar arquivo, enviar email, chamar API),
- ou é grande demais para caber num método de model.
"""
```

> **Por que um arquivo, não uma pasta `services/`?** Porque ainda não tem código. **YAGNI**: não criar abstração antes da dor. Quando o `services.py` passar de ~300 linhas, vira pasta com submódulos. Não antes.

---

## 3. Botão "Finalizar" no detalhe — colhendo o método do model

Para ver o `post.finalizar()` em ação, vamos colocar um botão na tela.

`posts/views.py` — adicione no fim:

```python
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST


@require_POST
def post_finalizar(request, pk):
    post = get_object_or_404(Post, pk=pk, autor=request.user)
    post.finalizar()
    return redirect('posts:detail', pk=pk)
```

| Detalhe | Por quê |
|---|---|
| `@require_POST` | Mudança de estado **nunca** em GET. Se alguém acessar a URL no navegador (GET), recebe 405 |
| `get_object_or_404(..., autor=request.user)` | Mesma proteção da Aula 05: post de outro usuário simplesmente não existe |
| Sem `if`, sem `try`, sem 5 linhas — | Toda regra (validar dono, mudar status, salvar) está delegada. A view só orquestra |

`posts/urls.py` — adicione a rota:

```python
path('<int:pk>/finalizar/', views.post_finalizar, name='finalizar'),
```

`posts/templates/posts/detail.html` — adicione antes do botão de excluir, dentro do bloco de ações:

```html
{% if not post.esta_finalizado %}
    <form method="post" action="{% url 'posts:finalizar' post.pk %}" class="inline">
        {% csrf_token %}
        <button type="submit" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
            Marcar como finalizado
        </button>
    </form>
{% endif %}
```

Recarregue: o botão aparece em posts em progresso, some quando o post fica finalizado. Clique — o status muda. Tudo isso atravessou a hierarquia inteira: template → view → model.

---

## 4. Anti-padrões para evitar

| Anti-padrão | Por que dói | Como sair |
|---|---|---|
| **View gigante** | View vira misto de regras de domínio, validação e renderização. Difícil de testar e ler | Mover regra para model/services |
| **Service para tudo** | Cada operação trivial vira `posts/services/criar_post.py`. Quatro arquivos para fazer o que `Post(...).save()` faz | Service só com efeito colateral ou orquestração real |
| **Model "deus"** | Tudo no model, inclusive envio de email, geração de PDF, integração com Stripe | Mover efeitos colaterais para services |
| **Lógica em template** | `{% if post.status == 'em_progresso' and post.criado_em > some_date %}...` | Subir para `@property` no model |

---

## 5. A trilha daqui em diante

Nas próximas aulas, **cada decisão segue essa hierarquia**:

| Aula | Demanda | Onde vai morar | Por quê |
|---|---|---|---|
| 07 — Upload | Validar tamanho da imagem | `clean_imagem` no **form** | Validação de **input do usuário** vive no form. O model nem chega a ver o arquivo se for inválido |
| 08 — PDF | Gerar PDF a partir do post | Função em **`services.py`** | Tem efeito colateral (renderiza arquivo) e usa biblioteca externa (WeasyPrint). Não é responsabilidade do model |

Você vai ver as duas aulas chamarem essa hierarquia diretamente.

---

## 6. Quando quebrar a regra

Toda regra é uma **heurística**, não uma lei. Casos comuns onde se sai do padrão:

- **Protótipo descartável** — escreva tudo na view. Você vai jogar fora.
- **Regra realmente trivial** — `if post.titulo` direto no template. Não vale criar `@property` para uma comparação de 3 caracteres.
- **Performance** — às vezes uma query manual em `views.py` é mais rápida que três métodos encadeados de QuerySet. Otimize **depois** de medir.

A regra é: comece simples, suba quando doer. Não suba antes.

---

## Exercício

1. Adicione `esta_finalizado` (`@property`) e `finalizar()` (método) em `Post`.
2. Crie `PostQuerySet` com `do_usuario`, `em_progresso`, `finalizados`. Registre como manager.
3. Atualize `OwnedQuerysetMixin` para usar `.do_usuario(self.request.user)`.
4. Atualize o template da lista para usar `post.esta_finalizado`.
5. Crie `posts/services.py` vazio (com o docstring).
6. Implemente o botão "Marcar como finalizado" no detalhe (view, URL, template).
7. Teste: crie posts, finalize um, veja o badge mudar de cor e o botão sumir. Tente acessar `/posts/<id>/finalizar/` em GET no navegador → 405.
8. (Opcional) Abra o `python manage.py shell` e brinque com o vocabulário novo:
   ```python
   from posts.models import Post
   from accounts.models import User
   u = User.objects.first()
   Post.objects.do_usuario(u).em_progresso().count()
   ```

---

## 🔁 Vindo do Rails

Boa notícia: esta é a aula **mais parecida** com Rails de toda a trilha. A filosofia "fat model, skinny controller" é literalmente a mesma — só muda nome e sintaxe.

| Conceito | Rails | Django |
|---|---|---|
| Filosofia | "Fat model, skinny controller" | "Fat model, skinny view" (idêntico) |
| Métodos de instância | `def finalizar; ...; end` no model | `def finalizar(self): ...` no model |
| Atributo derivado | método sem parênteses no Ruby (`def esta_finalizado?`) | `@property` no Python (`def esta_finalizado(self): ...`) |
| Convenção de "predicado" | sufixo `?` (`finalizado?`) | prefixo `esta_`/`is_`/`has_` (sem `?` em Python) |
| Update parcial | `post.update_columns(status: ...)` (sem callbacks) ou `post.update(status: ...)` (com) | `post.save(update_fields=['status'])` |
| Filtro nomeado | `scope :do_usuario, ->(u) { where(autor: u) }` | método em `QuerySet` customizado: `def do_usuario(self, user): return self.filter(autor=user)` |
| Encadeamento de scopes | `Post.do_usuario(u).em_progresso` | `Post.objects.do_usuario(u).em_progresso()` |
| Lazy queries | Scopes são preguiçosos (`to_a` materializa) | QuerySets são preguiçosos (`list(qs)` ou iteração materializa) |
| Service object | `app/services/gerar_pdf_do_post.rb` (PORO) | `posts/services.py` com função (não classe) |
| Convenção de service | Classe + `.call(post)` (Trailblazer/Interactor) | Função simples (`gerar_pdf_do_post(post)`) |
| Validação no model vs no form | `validates :titulo, presence: true` (model) | Pode ser no `Model.clean()` ou no `Form.clean_titulo()` (Django separa: form é input, model é invariante) |
| Restrição de método HTTP | Definida em `routes.rb` (`post '/foo'`) | `@require_POST` ou `@require_http_methods(['POST'])` na view |
| 404 automático | `Post.find(id)` levanta `RecordNotFound` → 404 | `get_object_or_404(Post, pk=id)` levanta `Http404` → 404 |

> 💎 **`@property` ≠ método sem parênteses.** Em Ruby, `def esta_finalizado?; ...; end` é apenas um método — você invoca como `post.esta_finalizado?` sem parênteses **porque Ruby permite isso para qualquer método**. Em Python, `def esta_finalizado(self): ...` é um método e exige `post.esta_finalizado()` com parênteses. Para conseguir `post.esta_finalizado` (sem `()`), você precisa do decorator `@property`. Use quando o "atributo" é puramente derivado dos campos.

> 💎 **Use prefixos, não `?`.** Python não aceita `?` em nome de identificador. A convenção da comunidade é `is_*`, `has_*`, `can_*` ou (em PT-BR) `esta_*`, `tem_*`, `pode_*`. Evite o sufixo `_p` herdado de Lisp — ninguém usa em Python.

> 💎 **`update_fields` é o `update_columns` parcial.** Ambos pulam callbacks/signals genéricos quando você passa `update_fields=['x']`. A diferença: no Rails, `update_columns` **sempre** pula callbacks; em Django, `save(update_fields=...)` continua disparando o signal `post_save` (mas com a lista do que mudou). Saber o que sua stack faz nesse momento é importante quando há listeners.

> 💎 **`PostQuerySet.as_manager()` é "scopes em uma classe à parte".** Em Rails, o scope mora dentro do model. Em Django, você cria uma classe externa e faz `objects = PostQuerySet.as_manager()` — pareceria mais cerimônia, mas você ganha dois benefícios: (1) testar o queryset isoladamente e (2) métodos com lógica complexa virando código Python normal, sem o limite de "uma linha de lambda" que scopes Rails tendem a empurrar.

> 💎 **Service como função, não classe.** A comunidade Rails se acostumou com `GerarPdfDoPost.new(post).call` ou `GerarPdfDoPost.call(post)` (Interactor, Trailblazer). Python é menos cerimonioso: `def gerar_pdf_do_post(post): ...` faz o mesmo trabalho com menos boilerplate. Use classe **só** se precisar manter estado entre chamadas — caso raríssimo.

> 💎 **Validação: form vs model.** Em Rails, validação fica no model (`validates`) e o form/strong params só filtra atributos. Em Django, há **dois lugares** para validar: `Form.clean_<campo>()` (input do usuário) e `Model.clean()` (invariante do domínio). Regra: se o erro **só** faz sentido no contexto de um formulário (ex: "imagem maior que 5 MB"), vai pro form. Se o erro existiria **mesmo se o registro fosse criado via console** (ex: "data de fim antes da data de início"), vai pro model.

---

## Próxima aula

[Aula 07 — Upload de imagem no post](aula-07-upload-de-imagem.md). Vamos aplicar a hierarquia: validação de input → form.
