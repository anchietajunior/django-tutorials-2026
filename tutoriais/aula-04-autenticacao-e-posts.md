# Aula 04 — Autenticação + CRUD de Posts

## Objetivo

Sair do projeto vazio para um sistema com **dois mundos**:

- **Página pública** (`/`) — qualquer pessoa acessa.
- **Área privada** (`/posts/`) — só usuário logado entra. Lá ele cria, lista, edita e exclui **Posts** (título, descrição e status).

```
[ Visitante ]──► /             (home pública)
                 │
                 └──► /contas/entrar/   ──► login
                                          │
[ Usuário logado ]──► /posts/  ◄──────────┘  (CRUD)
```

> Nesta aula **todos os posts ficam visíveis para todo usuário logado**. A separação "cada um vê só os seus" é o tema da [Aula 05](aula-05-controle-de-acesso.md).

---

## 1. Dois apps, dois assuntos

Até aqui temos só `config/` (settings, urls, view de boas-vindas). Agora vamos agrupar código por assunto, criando **dois apps**:

| App | Cuida de | Models |
|---|---|---|
| `accounts` | Cadastro, login, logout, modelo de usuário | `User` |
| `posts` | CRUD da entidade Post | `Post` |

> **O que é um app?** Uma pasta com `models.py`, `views.py`, `urls.py`, `templates/` etc. É a unidade de organização do Django. Crie um quando perceber que tem **3+ arquivos sobre o mesmo assunto**.

---

## Parte A — Autenticação

### 2. Criar o app `accounts`

```bash
python manage.py startapp accounts
```

Gera a pasta `accounts/` com vários arquivos prontos.

### 3. Model: User customizado

`accounts/models.py`:

```python
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass
```

**Por que User customizado já agora?** A documentação oficial recomenda criar `AUTH_USER_MODEL` antes da primeira migration, mesmo vazio. Adiar significa reset de banco depois. Herdamos de `AbstractUser` — ganhamos `username`, `email`, `password`, `is_staff` etc. de graça e ficamos com a porta aberta para campos futuros (`avatar`, `bio`...).

### 4. Settings: registrar app + auth

Em `config/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps do projeto
    'accounts',
]

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'posts:list'
LOGOUT_REDIRECT_URL = 'home'
```

| Setting | Função |
|---|---|
| `AUTH_USER_MODEL` | Diz ao Django qual model usar como User |
| `LOGIN_URL` | Para onde redirecionar visitantes que tentarem acessar área privada |
| `LOGIN_REDIRECT_URL` | Aonde ir após login bem-sucedido (lista de posts) |
| `LOGOUT_REDIRECT_URL` | Aonde ir após logout (volta pra home pública) |

### 5. Admin do User

`accounts/admin.py`:

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

admin.site.register(User, UserAdmin)
```

Reaproveitamos a `UserAdmin` padrão — todas as funcionalidades (criar, mudar senha, gerenciar permissões) sem escrever código.

### 6. Migrate + superuser

```bash
python manage.py makemigrations accounts
python manage.py migrate
python manage.py createsuperuser
```

Anote o usuário/senha. Eles dão acesso a `/admin/`.

### 7. Form de signup

`accounts/forms.py`:

```python
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']
```

`UserCreationForm` já valida senha forte e confirmação. Só trocamos o model.

### 8. View de signup

`accounts/views.py`:

```python
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SignupForm


class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')
```

Login e logout já vêm prontos do Django (`LoginView`, `LogoutView`) — vamos usá-los direto no `urls.py`.

### 9. URLs do app

`accounts/urls.py`:

```python
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path(
        'entrar/',
        LoginView.as_view(template_name='accounts/login.html'),
        name='login',
    ),
    path('sair/', LogoutView.as_view(), name='logout'),
    path('cadastrar/', views.SignupView.as_view(), name='signup'),
]
```

Em `config/urls.py`, registre o include:

```python
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('accounts.urls')),
    path('', views.home, name='home'),
]
```

### 10. Templates de auth

```bash
mkdir -p accounts/templates/accounts
```

`accounts/templates/accounts/login.html`:

```html
{% extends 'base.html' %}
{% block title %}Entrar{% endblock %}

{% block content %}
<div class="max-w-md mx-auto bg-white p-8 rounded-lg shadow">
    <h1 class="text-2xl font-bold mb-6 text-center">Entrar</h1>

    <form method="post" class="space-y-4">
        {% csrf_token %}

        {% if form.non_field_errors %}
            <div class="bg-red-50 text-red-800 p-3 rounded">{{ form.non_field_errors }}</div>
        {% endif %}

        {% for field in form %}
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ field.label }}</label>
                <input type="{{ field.field.widget.input_type }}"
                       name="{{ field.name }}"
                       class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:border-blue-500">
                {% if field.errors %}
                    <div class="text-sm text-red-600 mt-1">{{ field.errors }}</div>
                {% endif %}
            </div>
        {% endfor %}

        <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
            Entrar
        </button>
    </form>

    <p class="text-center text-sm text-gray-600 mt-4">
        Não tem conta? <a href="{% url 'accounts:signup' %}" class="text-blue-600 hover:underline">Cadastre-se</a>
    </p>
</div>
{% endblock %}
```

`accounts/templates/accounts/signup.html`:

```html
{% extends 'base.html' %}
{% block title %}Cadastrar{% endblock %}

{% block content %}
<div class="max-w-md mx-auto bg-white p-8 rounded-lg shadow">
    <h1 class="text-2xl font-bold mb-6 text-center">Criar conta</h1>

    <form method="post" class="space-y-4">
        {% csrf_token %}

        {% for field in form %}
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ field.label }}</label>
                {{ field }}
                {% if field.help_text %}
                    <p class="text-xs text-gray-500 mt-1">{{ field.help_text|safe }}</p>
                {% endif %}
                {% if field.errors %}
                    <div class="text-sm text-red-600 mt-1">{{ field.errors }}</div>
                {% endif %}
            </div>
        {% endfor %}

        <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
            Cadastrar
        </button>
    </form>

    <p class="text-center text-sm text-gray-600 mt-4">
        Já tem conta? <a href="{% url 'accounts:login' %}" class="text-blue-600 hover:underline">Entrar</a>
    </p>
</div>
{% endblock %}
```

### 11. Navbar reativa em `base.html`

Em `templates/base.html`, troque `{% block nav %}{% endblock %}` por:

```html
{% if user.is_authenticated %}
    <a href="{% url 'posts:list' %}" class="text-gray-700 hover:text-blue-600">Meus posts</a>
    <span class="text-gray-500">Olá, {{ user.username }}</span>
    <form method="post" action="{% url 'accounts:logout' %}" class="inline">
        {% csrf_token %}
        <button type="submit" class="text-gray-700 hover:text-red-600">Sair</button>
    </form>
{% else %}
    <a href="{% url 'accounts:login' %}" class="text-gray-700 hover:text-blue-600">Entrar</a>
    <a href="{% url 'accounts:signup' %}" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        Cadastrar
    </a>
{% endif %}
```

> **Por que logout via POST?** Versões recentes do Django só aceitam logout em POST (evita logout via link forjado).

A navbar agora **se adapta**: visitante vê "Entrar/Cadastrar"; logado vê "Meus posts/Sair".

---

## Parte B — CRUD de Posts

### 12. Criar o app `posts`

```bash
python manage.py startapp posts
```

Registre em `config/settings.py`:

```python
INSTALLED_APPS = [
    # ... os do Django
    'accounts',
    'posts',
]
```

### 13. Model `Post`

`posts/models.py`:

```python
from django.db import models


class Post(models.Model):
    class Status(models.TextChoices):
        EM_PROGRESSO = 'em_progresso', 'Em progresso'
        FINALIZADO = 'finalizado', 'Finalizado'

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

| Detalhe | Função |
|---|---|
| `TextChoices` | Forma idiomática do Django para enums em campos `CharField`. Cada item vira uma constante (`Post.Status.FINALIZADO`) e ganha label legível |
| `default=Status.EM_PROGRESSO` | Todo post nasce "em progresso" |
| `auto_now_add` | Gravado uma única vez na criação |
| `ordering = ['-criado_em']` | Lista do mais novo para o mais antigo |

### 14. Migration

```bash
python manage.py makemigrations posts
python manage.py migrate
```

### 15. Admin do Post

`posts/admin.py`:

```python
from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'status', 'criado_em']
    list_filter = ['status']
    search_fields = ['titulo', 'descricao']
```

Acesse `/admin/` e crie um post de teste para validar antes mesmo de fazer as views.

### 16. Form

`posts/forms.py`:

```python
from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'descricao', 'status']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'w-full border rounded px-3 py-2',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'w-full border rounded px-3 py-2',
                'rows': 5,
            }),
            'status': forms.Select(attrs={
                'class': 'w-full border rounded px-3 py-2',
            }),
        }
```

`ModelForm` gera o formulário a partir do model. Os `widgets` injetam classes Tailwind nos inputs.

### 17. Views CBV — o CRUD inteiro

`posts/views.py`:

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .forms import PostForm
from .models import Post


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'posts/list.html'
    context_object_name = 'posts'


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'posts/detail.html'
    context_object_name = 'post'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/form.html'
    success_url = reverse_lazy('posts:list')


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/form.html'
    success_url = reverse_lazy('posts:list')


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/confirm_delete.html'
    success_url = reverse_lazy('posts:list')
```

| Mixin/CBV | Função |
|---|---|
| `LoginRequiredMixin` | Se não estiver logado, redireciona para `LOGIN_URL`. Esta é a "porta da área privada" |
| `ListView` | GET → renderiza template com a lista |
| `DetailView` | GET → mostra um registro pelo `pk` da URL |
| `CreateView`/`UpdateView` | GET → form vazio/preenchido. POST → valida e salva |
| `DeleteView` | GET → tela de confirmação. POST → apaga |

### 18. URLs do app

`posts/urls.py`:

```python
from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.PostListView.as_view(), name='list'),
    path('novo/', views.PostCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.PostUpdateView.as_view(), name='update'),
    path('<int:pk>/excluir/', views.PostDeleteView.as_view(), name='delete'),
]
```

Em `config/urls.py`:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('accounts.urls')),
    path('posts/', include('posts.urls')),
    path('', views.home, name='home'),
]
```

### 19. Templates do CRUD

```bash
mkdir -p posts/templates/posts
```

`posts/templates/posts/list.html`:

```html
{% extends 'base.html' %}
{% block title %}Meus posts{% endblock %}

{% block content %}
<div class="flex items-center justify-between mb-6">
    <h1 class="text-2xl font-bold">Posts</h1>
    <a href="{% url 'posts:create' %}" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        Novo post
    </a>
</div>

{% if posts %}
    <ul class="space-y-3">
        {% for post in posts %}
            <li class="bg-white p-4 rounded shadow flex items-center justify-between">
                <div>
                    <a href="{% url 'posts:detail' post.pk %}" class="text-lg font-semibold text-blue-600 hover:underline">
                        {{ post.titulo }}
                    </a>
                    <span class="ml-2 text-xs px-2 py-1 rounded
                        {% if post.status == 'finalizado' %}bg-green-100 text-green-800{% else %}bg-yellow-100 text-yellow-800{% endif %}">
                        {{ post.get_status_display }}
                    </span>
                </div>
                <div class="text-sm text-gray-500">{{ post.criado_em|date:"d/m/Y H:i" }}</div>
            </li>
        {% endfor %}
    </ul>
{% else %}
    <p class="text-gray-600">Nenhum post ainda. <a href="{% url 'posts:create' %}" class="text-blue-600 hover:underline">Criar o primeiro</a>.</p>
{% endif %}
{% endblock %}
```

`posts/templates/posts/detail.html`:

```html
{% extends 'base.html' %}
{% block title %}{{ post.titulo }}{% endblock %}

{% block content %}
<article class="bg-white p-6 rounded shadow max-w-3xl mx-auto">
    <h1 class="text-3xl font-bold mb-2">{{ post.titulo }}</h1>
    <p class="text-sm text-gray-500 mb-4">
        {{ post.get_status_display }} · {{ post.criado_em|date:"d/m/Y H:i" }}
    </p>
    <div class="prose mb-6 whitespace-pre-line">{{ post.descricao }}</div>

    <div class="flex gap-3">
        <a href="{% url 'posts:update' post.pk %}" class="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600">Editar</a>
        <a href="{% url 'posts:delete' post.pk %}" class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Excluir</a>
        <a href="{% url 'posts:list' %}" class="text-gray-600 hover:underline self-center ml-auto">Voltar</a>
    </div>
</article>
{% endblock %}
```

`posts/templates/posts/form.html` (compartilhado entre create e update):

```html
{% extends 'base.html' %}
{% block title %}{% if form.instance.pk %}Editar{% else %}Novo{% endif %} post{% endblock %}

{% block content %}
<div class="max-w-2xl mx-auto bg-white p-6 rounded shadow">
    <h1 class="text-2xl font-bold mb-6">
        {% if form.instance.pk %}Editar post{% else %}Novo post{% endif %}
    </h1>

    <form method="post" class="space-y-4">
        {% csrf_token %}

        {% for field in form %}
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ field.label }}</label>
                {{ field }}
                {% if field.errors %}
                    <div class="text-sm text-red-600 mt-1">{{ field.errors }}</div>
                {% endif %}
            </div>
        {% endfor %}

        <div class="flex gap-3">
            <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Salvar</button>
            <a href="{% url 'posts:list' %}" class="text-gray-600 hover:underline self-center">Cancelar</a>
        </div>
    </form>
</div>
{% endblock %}
```

`posts/templates/posts/confirm_delete.html`:

```html
{% extends 'base.html' %}
{% block title %}Excluir post{% endblock %}

{% block content %}
<div class="max-w-xl mx-auto bg-white p-6 rounded shadow">
    <h1 class="text-xl font-bold mb-4">Excluir post</h1>
    <p class="mb-6">Tem certeza que deseja excluir <strong>{{ post.titulo }}</strong>?</p>

    <form method="post">
        {% csrf_token %}
        <button type="submit" class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Sim, excluir</button>
        <a href="{% url 'posts:list' %}" class="text-gray-600 hover:underline ml-3">Cancelar</a>
    </form>
</div>
{% endblock %}
```

---

## 20. Testar o fluxo completo

```bash
python manage.py runserver
```

1. Abra `/` deslogado → vê a home pública.
2. Clique em **Cadastrar** → crie um usuário.
3. É redirecionado para o login → entre com o usuário recém-criado.
4. Após login, cai em `/posts/` (a `LOGIN_REDIRECT_URL` que configuramos).
5. Clique em **Novo post** → preencha título, descrição, status → salve.
6. O post aparece na lista. Clique nele → veja o detalhe.
7. Edite, depois exclua. Clique em **Sair** → volta deslogado para `/`.
8. Tente acessar `/posts/` deslogado → é mandado para `/contas/entrar/`.

---

## Estrutura final do projeto

```
app/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── views.py
├── accounts/
│   ├── models.py        ← User(AbstractUser)
│   ├── forms.py         ← SignupForm
│   ├── views.py         ← SignupView
│   ├── urls.py
│   ├── admin.py
│   └── templates/accounts/{login,signup}.html
├── posts/
│   ├── models.py        ← Post(titulo, descricao, status)
│   ├── forms.py         ← PostForm
│   ├── views.py         ← 5 CBVs (List/Detail/Create/Update/Delete)
│   ├── urls.py
│   ├── admin.py
│   └── templates/posts/{list,detail,form,confirm_delete}.html
└── templates/
    ├── base.html        ← navbar reativa ao login
    └── home.html
```

---

## Exercício

1. Crie os dois apps (`accounts`, `posts`) e registre em `INSTALLED_APPS`.
2. Implemente `User(AbstractUser)`, `AUTH_USER_MODEL`, signup/login/logout funcionando.
3. Implemente o model `Post` com `TextChoices` para status.
4. Faça o CRUD completo com CBVs e `LoginRequiredMixin`.
5. Teste: deslogado → não acessa `/posts/`. Logado → CRUD funciona ponta a ponta.
6. (Opcional) Crie um segundo usuário e veja que **ele consegue ver e editar os posts do primeiro** — esse é exatamente o problema que vamos resolver na próxima aula.

---

## 🔁 Vindo do Rails

Esta é a aula mais densa em paralelos — Django toma decisões diferentes do Rails em quase todas as camadas.

| Conceito | Rails | Django |
|---|---|---|
| Unidade de organização | Engine (`rails plugin new --mountable`) ou só pastas em `app/` | **App** (`python manage.py startapp accounts`) |
| Carregamento | Tudo em `app/` é autoload pelo Zeitwerk | App **precisa** ser registrado em `INSTALLED_APPS` |
| Modelo de usuário | Devise + `User < ApplicationRecord` (ou `has_secure_password` puro) | `AbstractUser` herdado num `User(AbstractUser)` próprio |
| Trocar User padrão | `Devise.user_class = ...` (raro) | `AUTH_USER_MODEL = 'accounts.User'` (canônico, **antes da 1ª migration**) |
| Migration de coluna | Você escreve à mão (`add_column :users, :nome, :string`) | `makemigrations` **detecta a diferença** entre model e DB e gera o arquivo |
| Aplicar migration | `rails db:migrate` | `python manage.py migrate` |
| Reverter | `rails db:rollback` | `python manage.py migrate accounts <numero_anterior>` |
| Criar admin | Console + `User.create!(admin: true)` ou seed | `python manage.py createsuperuser` (interativo) |
| Painel administrativo | `activeadmin`, `rails_admin`, `avo` (gem externa) | `django.contrib.admin` (built-in!) |
| Routes | `config/routes.rb` com DSL (`resources :posts`) | `urls.py` com lista de `path(...)` (sem DSL — Python puro) |
| Namespace de rotas | `namespace :accounts do ... end` | `path('contas/', include('accounts.urls'))` + `app_name = 'accounts'` |
| URL helper | `accounts_login_path` | `{% url 'accounts:login' %}` (string com prefixo do `app_name`) |
| Controller pattern | Métodos imperativos numa classe (`def show; end`) | **CBV** (`DetailView`, `CreateView`...) ou **FBV** (função recebendo `request`) |
| Form helpers | `form_with model: @post` + strong params | `ModelForm` (classe declarativa que gera campos do model) |
| Strong params | `params.require(:post).permit(:titulo, :descricao)` | `Meta.fields = ['titulo', 'descricao']` no `ModelForm` |
| CSRF | `<%= csrf_meta_tags %>` (auto em forms) | `{% csrf_token %}` (precisa colocar à mão em todo `<form>`) |
| Auth before_action | `before_action :authenticate_user!` (Devise) | `LoginRequiredMixin` (CBV) ou `@login_required` (FBV) |
| Usuário atual | `current_user` (Devise) | `request.user` (sempre disponível) |
| Logout | DELETE em `destroy_user_session_path` (Devise) | POST em `LogoutView` (Django 5+ exige POST) |

> 💎 **`INSTALLED_APPS` é registro explícito.** Em Rails, basta criar uma classe em `app/models/` que o Zeitwerk acha. No Django, **se o app não estiver listado em `INSTALLED_APPS`, o `migrate` ignora os models e o `runserver` ignora os templates**. É a primeira armadilha do "criei o app e nada acontece".

> 💎 **`makemigrations` é mágico, `migrate` não.** `rails generate migration` cria um arquivo **vazio** que você preenche. `python manage.py makemigrations` **lê seus models, compara com o estado anterior e gera o arquivo já preenchido**. Você quase nunca abre uma migration para escrever — só para revisar ou customizar.

> 💎 **CBV é uma abstração sem paralelo direto.** `ListView`, `DetailView`, `CreateView` etc. são classes que implementam o ciclo CRUD genérico via mixins. O equivalente Rails seria a gem `inherited_resources` (que poucos usam — Rails prefere o controller imperativo). Se você estranhar o estilo, saiba que Django também aceita FBV (função `def home(request): ...`) e os dois coexistem na mesma app.

> 💎 **`app_name` é como `as: 'accounts'` em rotas com namespace.** O `'accounts:login'` vira a chave de lookup do helper. Sem o `app_name`, dois apps com URL chamada `'login'` colidem — exatamente o problema que `namespace :accounts do ... end` resolve em Rails.

> 💎 **`ModelForm` ≠ `form_with`.** `form_with model: @post` no Rails é um **helper de view** que renderiza HTML. `ModelForm` no Django é uma **classe Python** que valida dados, renderiza widgets e converte cleaned data para `Model.objects.create(**form.cleaned_data)`. Mais perto de `ActiveRecord::Validations` + Form Object (`reform`, `dry-validation`) juntos do que de `form_with`.

> 💎 **Admin já vem incluído.** O Django Admin (`/admin/`) é parte do framework, não uma gem. Você registra um model com `@admin.register(Post)` e ganha CRUD completo gratuitamente. O paralelo Rails é uma gem externa — `activeadmin`, `rails_admin`, `avo`. O preço: o admin é menos customizável que `avo`, e te pune se você sair do feijão com arroz.

---

## Próxima aula

[Aula 05 — Controle de acesso: cada um vê só os seus posts](aula-05-controle-de-acesso.md).
