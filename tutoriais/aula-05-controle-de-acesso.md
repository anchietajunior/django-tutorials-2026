# Aula 05 — Controle de acesso: cada um vê só os seus posts

## Objetivo

Hoje todo usuário logado vê (e edita, e apaga) os posts de **todo mundo**. Vamos mudar isso: cada post pertence a um **dono** (`autor`), e cada usuário só consegue listar/ver/editar/excluir os **seus**.

```
[ Post ] ──FK──► [ User ]
       (autor)
```

Três camadas de proteção, da mais fraca para a mais forte:

1. **Filtro no QuerySet** — não aparece na lista quem não é seu.
2. **Filtro no objeto** — `get_object` só devolve se for seu (caso alguém digite `/posts/42/` na mão).
3. **Atribuição automática do autor** — ao criar, dono = `request.user` (não confiamos no form).

---

## 1. Adicionar o campo `autor` ao Post

Em `posts/models.py`, importe e adicione o campo:

```python
from django.conf import settings
from django.db import models


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
```

| Detalhe | Por quê |
|---|---|
| `settings.AUTH_USER_MODEL` | **Nunca** importe `User` diretamente — a referência via settings funciona com qualquer User customizado |
| `on_delete=models.CASCADE` | Apagou o usuário, somem os posts dele |
| `related_name='posts'` | Permite escrever `usuario.posts.all()` para pegar os posts de um usuário |

---

## 2. Migration com posts já existentes

Se você já tem posts criados na Aula 03, eles **não têm autor**. Ao rodar:

```bash
python manage.py makemigrations posts
```

O Django pergunta:

```
You are trying to add a non-nullable field 'autor' to post without a default;
1) Provide a one-off default now
2) Quit and let me add a default in models.py
```

Escolha **1** e digite `1` (ID do superuser que você criou). Isso vincula os posts órfãos ao admin. Depois:

```bash
python manage.py migrate
```

> **Em produção** essa decisão não seria assim simples — exigiria uma data migration cuidadosa. Em sala de aula, o atalho é aceitável.

---

## 3. Atualizar o admin

`posts/admin.py`:

```python
from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'status', 'criado_em']
    list_filter = ['status', 'autor']
    search_fields = ['titulo', 'descricao']
```

---

## 4. Tirar o `autor` do form

O usuário **não escolhe** o dono — é sempre ele mesmo. Em `posts/forms.py` mantenha como estava (sem `autor` em `fields`). Se o aluno tentar adicionar, vire o problema do avesso: deixe explícito.

```python
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'descricao', 'status']  # autor NÃO entra
        widgets = { ... }
```

---

## 5. Filtrar e proteger as views

Em `posts/views.py`:

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .forms import PostForm
from .models import Post


class OwnedQuerysetMixin:
    """Restringe o queryset aos posts do usuário logado."""

    def get_queryset(self):
        return super().get_queryset().filter(autor=self.request.user)


class PostListView(LoginRequiredMixin, OwnedQuerysetMixin, ListView):
    model = Post
    template_name = 'posts/list.html'
    context_object_name = 'posts'


class PostDetailView(LoginRequiredMixin, OwnedQuerysetMixin, DetailView):
    model = Post
    template_name = 'posts/detail.html'
    context_object_name = 'post'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/form.html'
    success_url = reverse_lazy('posts:list')

    def form_valid(self, form):
        form.instance.autor = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, OwnedQuerysetMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/form.html'
    success_url = reverse_lazy('posts:list')


class PostDeleteView(LoginRequiredMixin, OwnedQuerysetMixin, DeleteView):
    model = Post
    template_name = 'posts/confirm_delete.html'
    success_url = reverse_lazy('posts:list')
```

### O que mudou — peça por peça

| Mudança | Por quê |
|---|---|
| `OwnedQuerysetMixin` | Filtra `Post.objects.filter(autor=request.user)` no `get_queryset`. Como `DetailView`, `UpdateView` e `DeleteView` chamam `get_object()` em cima desse queryset, **um post de outro usuário simplesmente não existe para essa view** — devolve 404, não 403. Mais limpo: o atacante nem sabe que o ID existe |
| `form_valid` no `CreateView` | Antes de salvar, atribui `form.instance.autor = self.request.user`. Mesmo que alguém forje um POST com outro `autor`, a view sobrescreve |
| `CreateView` **sem** `OwnedQuerysetMixin` | Faz sentido: criação não consulta nada — não há queryset a filtrar |

> **Por que mixin e não copiar `get_queryset` em cada view?** Porque a regra é a mesma nas quatro views. Mixin = uma fonte da verdade. Mexer aqui muda tudo.

---

## 6. Esconder ações que o usuário não pode fazer

O backend já está seguro. Falta o frontend não mentir: o usuário não deve ver botões para posts que não são dele (e graças ao filtro do queryset, ele nem vê esses posts no template — mas se um dia houver listas mistas, é aqui que se trata).

No `detail.html` e `list.html`, todo post listado já é do usuário (porque o queryset filtra). Nada a mudar agora — o template está consistente com a regra. Se você quiser ser explícito, pode reforçar com um `if`:

```html
{% if post.autor == user %}
    <a href="{% url 'posts:update' post.pk %}">Editar</a>
{% endif %}
```

Mas, na prática, o filtro do queryset já garante que `post.autor == user` é sempre verdade aqui.

---

## 7. Testar de verdade

```bash
python manage.py runserver
```

1. Faça login com o **usuário A** → crie 2 posts ("A1", "A2").
2. **Sair**. Faça signup de um **usuário B** → entre.
3. `/posts/` → lista vazia. ✅
4. Crie um post "B1" no usuário B → só "B1" aparece.
5. Tente acessar **na URL** o post do A: digite `/posts/1/` (assumindo que A1 tem id=1).
6. Resultado esperado: **404 — Page not found**. ✅
7. Mesmo teste com `/posts/1/editar/` e `/posts/1/excluir/` → 404. ✅
8. Faça logout, entre como A → seus posts continuam lá.

Se algum desses passos retornar a página em vez de 404, falta filtro em alguma view — revise o mixin.

---

## 8. Por que 404 em vez de 403?

| Resposta | Mensagem implícita |
|---|---|
| `403 Forbidden` | "Existe esse recurso, mas você não pode" — vaza informação |
| `404 Not Found` | "Não existe pra você" — não confirma nem nega |

Filtrar no `get_queryset` faz o Django responder 404 naturalmente, sem código extra. É mais seguro **e** mais simples.

---

## Exercício

1. Adicione o campo `autor` ao `Post` e rode a migration (escolhendo um default para os posts existentes).
2. Atualize `PostAdmin` para mostrar o autor.
3. Implemente `OwnedQuerysetMixin` e aplique em List/Detail/Update/Delete.
4. Sobrescreva `form_valid` no `PostCreateView` para atribuir `autor = request.user`.
5. Faça os 8 testes da seção 7 — todos devem passar.
6. (Opcional) Adicione um teste automatizado: usuário B tenta acessar post de A via URL → espera 404.

---

## 🔁 Vindo do Rails

| Conceito | Rails | Django |
|---|---|---|
| Foreign key + associação | `belongs_to :autor, class_name: 'User'` (do lado do Post) | `autor = ForeignKey(settings.AUTH_USER_MODEL, ...)` (do lado do Post) |
| Reverse association | `has_many :posts, dependent: :destroy` (do lado do User) | `related_name='posts'` no `ForeignKey` (sem precisar declarar nada no User) |
| Estratégia de delete | `dependent: :destroy` (no `has_many`) | `on_delete=models.CASCADE` (no `ForeignKey`, lado oposto!) |
| Referenciar `User` em FK | `belongs_to :user` (Rails sabe a classe pelo nome) | `settings.AUTH_USER_MODEL` (string lazy — funciona com `User` customizado) |
| Filtrar por dono | `current_user.posts` ou `Post.where(user: current_user)` | `Post.objects.filter(autor=request.user)` ou `request.user.posts.all()` |
| Autorização | Pundit / CanCanCan + `policy_scope(Post)` | Filtrar no `get_queryset` (resposta 404) ou checar `permission_required` (resposta 403) |
| Resposta a recurso de outro usuário | Pundit raises `NotAuthorizedError` → 403 (típico) | `get_queryset().filter(...)` faz o objeto **não existir** → 404 |
| Atribuir dono no create | `@post.user = current_user` antes do `save` | `form.instance.autor = self.request.user` em `form_valid` |

> 💎 **`on_delete` fica do lado "filho", não do "pai".** Em Rails, `dependent: :destroy` é declarado no `has_many :posts` (lado User). No Django, `on_delete=CASCADE` é declarado no `ForeignKey` (lado Post). A direção é invertida — pense "se o User sumir, o que acontece com **este** Post?" e a resposta vai onde o `ForeignKey` está.

> 💎 **`related_name` é o "nome" do `has_many`.** No Rails, `has_many :posts` cria `user.posts`. No Django, você não declara nada no `User` — o `related_name='posts'` no `ForeignKey` do Post é que cria `user.posts.all()`. Sem `related_name`, o default é `<model>_set` (`user.post_set.all()`) — feio, então sempre defina `related_name`.

> 💎 **Use `settings.AUTH_USER_MODEL`, NUNCA `from accounts.models import User`.** Importar `User` direto numa FK quebra projetos com User customizado e cria dependências circulares. Equivalente Rails: imagine que cada vez que um plugin referenciasse `User`, ele desse `require 'app/models/user'` em vez de só dizer `class_name: 'User'`. A string `'accounts.User'` é resolvida tarde (lazy) — sempre funciona.

> 💎 **A escolha 404 vs 403 é cultural.** Em Rails com Pundit, a convenção é responder **403** ("você existe mas não pode"). No Django, filtrar no queryset dá **404** ("para você, esse recurso não existe"). 404 vaza menos informação para um atacante (não confirma a existência do ID), e sai de graça do `get_queryset`. Se preferir 403 explícito, dá para usar `UserPassesTestMixin` ou pacotes como `django-rules` — análogos a Pundit.

> 💎 **Mixin é a "concern" do Django.** `OwnedQuerysetMixin` é uma classe sem `__init__` que herda à esquerda da CBV principal. Mesmo padrão de uma `concern` Rails (`include Authorizable`). A ordem importa: mixins **antes** da classe base na lista de herança.

---

## Próxima aula

[Aula 06 — Regras de negócio: onde colocar?](aula-06-regras-de-negocio.md).
