# Aula 04 — User Customizado + Autenticação

## Objetivo

Criar o **User customizado** (decisão importante para projetos sérios) e telas de **signup, login, logout** com Tailwind. Esta aula introduz ao mesmo tempo: criação de app, definição de Model, primeira migration, admin e CBVs.

```
[ app accounts ] → [ User(AbstractUser) ] → [ AUTH_USER_MODEL ] → [ migrate ] → [ telas ]
```

> **Por que User customizado já agora?** A documentação oficial do Django recomenda criar um `User` customizado **antes da primeira migration** mesmo que vazio. Adiar significa reset de banco depois.

---

## 1. O que é um "app" no Django?

Até agora todo o nosso código mora dentro de `config/`: settings, urls, uma view de boas-vindas. Funciona — mas a partir desta aula vamos ter **vários arquivos sobre o mesmo assunto**: model do usuário, formulário de cadastro, view de signup, templates de login... Tudo sobre autenticação.

Quando isso acontece, o Django pede para a gente **agrupar tudo num pacote**, chamado **app**. Um app é só uma pasta com arquivos relacionados:

```
accounts/
├── __init__.py     # marca a pasta como pacote Python
├── admin.py        # configuração do Django Admin
├── apps.py         # metadados do app (gerado automaticamente)
├── models.py       # tabelas do banco
├── views.py        # funções/classes que respondem a requisições
├── urls.py         # rotas (vamos criar)
└── templates/      # HTMLs (vamos criar)
```

A vantagem: tudo sobre autenticação fica num lugar só. Se um dia o sistema crescer, dá para reaproveitar o app inteiro em outro projeto.

> **Regra prática para iniciantes:** crie um app quando perceber que tem 3+ arquivos relacionados a um mesmo assunto. Para uma única página (como a home), não precisa.

### Criar o app

```bash
python manage.py startapp accounts
```

Esse comando gera a pasta `accounts/` com vários arquivos prontos. Vamos editá-los nas próximas seções.

---

## 2. Model: User customizado

`accounts/models.py`:

```python
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass
```

**Por que `AbstractUser`?** Herda tudo do User padrão (username, email, password, is_staff...). Ficamos com a porta aberta para adicionar campos depois (ex: `avatar`, `bio`) sem virar reset.

---

## 3. Configurar `settings.py`

Em `config/settings.py`, registre o novo app e ajuste as configurações de autenticação:

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
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
```

| Setting | Função |
|---|---|
| `'accounts'` em `INSTALLED_APPS` | Avisa o Django que existe esse app — sem isso ele ignora migrations e templates do app |
| `AUTH_USER_MODEL` | Diz ao Django qual model usar como User |
| `LOGIN_URL` | Para onde redirecionar usuários não autenticados |
| `LOGIN_REDIRECT_URL` | Para onde ir após login bem sucedido (`home` é o `name` da rota da Aula 03) |
| `LOGOUT_REDIRECT_URL` | Para onde ir após logout |

---

## 4. Admin do User

`accounts/admin.py`:

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

admin.site.register(User, UserAdmin)
```

Reaproveitamos a `UserAdmin` padrão — todas as funcionalidades (criar, editar permissões, mudar senha) sem escrever código.

---

## 5. Primeira migration + superuser

Agora podemos migrar pela primeira vez:

```bash
python manage.py makemigrations accounts
python manage.py migrate
```

Cria as tabelas internas do Django (auth, sessions, admin) **e** o `accounts_user`.

```bash
python manage.py createsuperuser
```

O comando vai pedir três informações no terminal:

```
Username: admin
Email address: admin@local.com
Password: ••••••••••
Password (again): ••••••••••
Superuser created successfully.
```

> **Senha curta dá aviso?** Se a senha for muito simples (`123`, por exemplo), o Django pergunta se você quer mesmo continuar. Para fins de aprendizado pode aceitar — em produção, NÃO.

---

## 6. Primeiro contato com o Django Admin

Você acabou de criar o **superuser**: um usuário com `is_staff=True` e `is_superuser=True`. Esses dois booleanos é que destravam a página `/admin/`. (Volte na conversa "Existe relação entre User e Admin?" se quiser revisar — é a mesma tabela, separada só por flags.)

Suba o servidor:

```bash
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/admin/`. Vai aparecer uma tela de login do Django Admin (não confunda com a tela de login que vamos construir nas próximas seções — essa é embutida).

Faça login com as credenciais do superuser. Depois do login, você cai num painel parecido com este:

```
Django administration                        Welcome, ADMIN. Log out

Site administration

  AUTHENTICATION AND AUTHORIZATION
  ──────────────────────────────────
  Groups                       + Add    ✎ Change
  Users                        + Add    ✎ Change
```

### O que cada peça significa

| Elemento | Função |
|---|---|
| **Groups** | Grupos de permissões (ex: "Editores", "Moderadores"). Não vamos usar agora |
| **Users** | Lista de usuários cadastrados — **é a sua tabela `accounts_user`**. Tem o `admin` que você acabou de criar |
| **+ Add** | Botão para criar uma nova linha no model |
| **✎ Change** | Lista todos os registros existentes |

> **Por que só aparece "Authentication and Authorization"?** Porque registramos só o `User` no `accounts/admin.py` (seção 4 acima). Quando criarmos o model `Categoria` na Aula 05 e registrarmos com `@admin.register(Categoria)`, ele vai aparecer aqui também.

### Explore um pouco

1. Clique em **Users** → você verá uma tabela com o `admin`
2. Clique no `admin` → abre o formulário de edição com TODOS os campos do User: username, password, email, first_name, last_name, **groups**, **user permissions**, **is_staff**, **is_superuser**, **is_active**, last login, date joined
3. Note que a senha aparece como hash (`pbkdf2_sha256$...`) e há um link "this form" para trocá-la — o Django nunca mostra senha em texto puro, nem para o admin
4. Volte para a página inicial e clique em **+ Add** ao lado de **Users** → o formulário é o mesmo `UserCreationForm` que vamos usar lá no signup

> **Importante:** o admin é uma ferramenta operacional poderosa. Você pode criar, editar e apagar dados diretamente sem passar pelas regras das suas views. Use com cuidado em produção e, mais importante: **só dê acesso ao admin (`is_staff=True`) para quem precisa**. Um usuário comum cadastrado via `/contas/cadastrar/` (que vamos criar a seguir) tem `is_staff=False` e simplesmente não consegue acessar `/admin/`.

### Sair do admin

Clique em "Log out" no canto superior direito. Vamos voltar a usar o admin na **Aula 05**, quando registrarmos o model `Categoria`.

---

## 7. Form de signup

`accounts/forms.py`:

```python
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']
```

Reutilizamos o `UserCreationForm` (já valida senha forte, confirmação, etc.) trocando o model para o nosso.

---

## 8. Views

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

| Detalhe | Função |
|---|---|
| `CreateView` | CBV para criação. Recebe form, renderiza no GET, salva no POST |
| `success_url` | Para onde ir após criar |
| `reverse_lazy` | Como `reverse`, mas avalia tarde (necessário em atributos de classe) |

---

## 9. URLs de auth

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

`LoginView` e `LogoutView` já vêm prontas do Django — só precisamos apontar o template do login.

Agora abra `config/urls.py` e adicione a inclusão das rotas de `accounts`. Esse arquivo já tinha a rota da home da Aula 03; só estamos acrescentando uma linha:

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

| Detalhe | Função |
|---|---|
| `include('accounts.urls')` | Diz "tudo que começar com `/contas/` é tratado pelo `accounts/urls.py`" |
| Ordem das rotas | `admin/` e `contas/` vêm antes da raiz — Django busca por prefixo, então a regra mais específica precisa vir primeiro |

---

## 10. Templates

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
                       {% if field.value %}value="{{ field.value }}"{% endif %}
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

---

## 11. Atualizar a navbar do `base.html`

Em `templates/base.html`, troque o `{% block nav %}{% endblock %}` por:

```html
{% if user.is_authenticated %}
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

> **Por que logout via POST?** Versões recentes do Django (5+) só aceitam logout em POST por segurança (evita CSRF de logout via link).

---

## 12. Testar

```bash
python manage.py runserver
```

1. Acesse `/contas/cadastrar/` → crie um usuário
2. Após salvar, é redirecionado para login
3. Faça login → volta para a home logado
4. A navbar muda: agora mostra "Olá, fulano" + botão Sair
5. Clica em Sair → volta para a home deslogado

---

## Exercício

1. Crie o app `accounts` com `User(AbstractUser)`
2. Configure `AUTH_USER_MODEL` e settings de auth
3. Registre `UserAdmin`
4. Rode `makemigrations` + `migrate` + `createsuperuser`
5. Crie `SignupForm`, `SignupView`, `accounts/urls.py`
6. Templates de login e signup
7. Atualize a navbar
8. Teste signup, login, logout

---

## Próxima aula

[Aula 05 — Categoria — Model + Admin](aula-05-categoria.md).
