# Aula 03 — Criando a Página Home e Adicionando TailwindCSS

## Onde estamos na arquitetura?

Nas aulas anteriores, criamos o projeto e configuramos o banco de dados. Agora vamos criar algo **visível** — a primeira página do projeto. Para isso, precisamos entender como o Django conecta URLs, Views e Templates.

```
Requisição do navegador → urls.py → View → Template (.html) → Resposta ao navegador
```

Também vamos integrar o **TailwindCSS** para estilizar as páginas sem escrever CSS manualmente.

---

## 1. Criando o Primeiro App

No Django, cada funcionalidade é organizada em **apps**. Um app é um módulo Python com responsabilidade sobre um domínio específico. Para a página Home, vamos criar um app chamado `core` — ele será responsável por páginas genéricas que não pertencem a nenhum domínio de negócio.

```bash
python manage.py startapp core
```

### Estrutura gerada

```
core/
├── __init__.py
├── admin.py         # Registro de models no admin
├── apps.py          # Configuração do app
├── migrations/      # Migrations do banco de dados
│   └── __init__.py
├── models.py        # Definição dos models
├── tests.py         # Testes automatizados
└── views.py         # Lógica das views
```

### Registrando o app no projeto

O Django **não detecta apps automaticamente**. Você precisa adicioná-lo na lista `INSTALLED_APPS` do `config/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps do projeto
    'core',
]
```

> **Por que registrar?** O Django usa essa lista para saber quais apps devem ter suas migrations detectadas, seus templates encontrados, seus arquivos estáticos coletados e seus models registrados. App não registrado é app invisível.

---

## 2. Criando a View

Uma **view** é uma função (ou classe) Python que recebe uma requisição HTTP e retorna uma resposta HTTP. É o "controlador" da arquitetura.

Abra `core/views.py`:

```python
from django.shortcuts import render


def home(request):
    return render(request, 'core/home.html')
```

### Linha a linha

| Linha | O que faz |
|---|---|
| `from django.shortcuts import render` | Importa a função `render`, que combina um template com dados e retorna HTML |
| `def home(request):` | Define a view. Toda view recebe `request` como primeiro parâmetro — é o objeto que contém tudo sobre a requisição (método, headers, dados do formulário, usuário logado, etc.) |
| `return render(request, 'core/home.html')` | Busca o template `core/home.html`, renderiza e retorna como resposta HTTP |

> **`request` é obrigatório.** Mesmo que você não use nada dele na view, ele sempre deve estar ali. É o contrato do Django com as views.

---

## 3. Configurando as URLs

O Django precisa saber qual URL aponta para qual view. Isso é feito em dois níveis.

### 3.1 URLs do app (`core/urls.py`)

Crie o arquivo `core/urls.py` (ele não vem criado automaticamente):

```python
from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
]
```

### Linha a linha

| Linha | O que faz |
|---|---|
| `from django.urls import path` | Importa a função que registra rotas |
| `from . import views` | Importa o módulo `views` do app atual (o ponto `.` significa "deste pacote") |
| `app_name = 'core'` | Define um **namespace** para as URLs deste app. Permite referenciar como `core:home` nos templates |
| `path('', views.home, name='home')` | URL vazia (raiz) aponta para a view `home`. O `name='home'` permite referenciar essa URL por nome em vez de hardcodar o caminho |

### 3.2 URLs do projeto (`config/urls.py`)

Agora inclua as URLs do app no roteador principal. Abra `config/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
```

### Como o roteamento funciona

Quando uma requisição chega (ex: `http://127.0.0.1:8000/`):

1. O Django consulta `config/urls.py`
2. A URL `/` não bate com `admin/`, então pula
3. A URL `/` bate com `''` → entra no `core/urls.py`
4. Dentro do `core/urls.py`, a URL vazia bate com `''` → chama `views.home`
5. A view renderiza o template e retorna o HTML

```
config/urls.py          core/urls.py          core/views.py
     ''        →             ''        →        home()
   admin/      →     (admin do Django)
```

---

## 4. Criando o Template

### 4.1 Configurando o diretório de templates

Abra `config/settings.py` e localize a variável `TEMPLATES`. Altere o `DIRS` para incluir uma pasta de templates na raiz:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # Adicione esta linha
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

> **`DIRS` vs `APP_DIRS`:** o `APP_DIRS: True` faz o Django procurar templates dentro de cada app (ex: `core/templates/`). O `DIRS` adiciona diretórios extras de busca. Usamos `DIRS` para templates globais (como o `base.html`) e `APP_DIRS` para templates específicos de cada app.

### 4.2 Estrutura de pastas dos templates

Crie a seguinte estrutura:

```
templates/               # Templates globais (definido em DIRS)
└── base.html            # Template base com a estrutura HTML

core/
└── templates/
    └── core/            # Subpasta com o nome do app (evita conflitos)
        └── home.html
```

> **Por que `core/templates/core/`?** Parece redundante, mas é uma convenção importante. Se dois apps tiverem um template chamado `home.html`, o Django pode carregar o errado. A subpasta com o nome do app funciona como namespace e evita conflitos.

Crie as pastas necessárias:

```bash
mkdir -p templates
mkdir -p core/templates/core
```

### 4.3 Template base (`templates/base.html`)

Este é o template "esqueleto" que todas as páginas vão herdar:

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Meu Projeto{% endblock %}</title>
</head>
<body>
    <header>
        <nav>
            <a href="{% url 'core:home' %}">Home</a>
        </nav>
    </header>

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer>
        <p>&copy; 2025 Meu Projeto</p>
    </footer>
</body>
</html>
```

### Entendendo as template tags

| Tag | O que faz |
|---|---|
| `{% block title %}...{% endblock %}` | Define um bloco que templates filhos podem sobrescrever. O conteúdo entre as tags é o valor padrão |
| `{% url 'core:home' %}` | Gera a URL da view `home` do app `core`. Usa o `app_name` e o `name` que definimos em `urls.py`. Nunca hardcode URLs |

### 4.4 Template da Home (`core/templates/core/home.html`)

```html
{% extends 'base.html' %}

{% block title %}Home{% endblock %}

{% block content %}
<h1>Bem-vindo ao Meu Projeto</h1>
<p>Esta é a página inicial.</p>
{% endblock %}
```

### Como a herança funciona

```
base.html (esqueleto)
├── block title → "Meu Projeto" (padrão)
└── block content → (vazio)

home.html (extends base.html)
├── block title → "Home" (sobrescreve)
└── block content → <h1>Bem-vindo...</h1> (preenche)
```

O resultado final é o HTML completo do `base.html` com os blocos preenchidos pelo `home.html`.

### 4.5 Testando

Rode o servidor e acesse `http://127.0.0.1:8000/`:

```bash
python manage.py runserver
```

Você deve ver a página com "Bem-vindo ao Meu Projeto" — sem estilo, apenas HTML puro. Agora vamos resolver isso com TailwindCSS.

---

## 5. Adicionando TailwindCSS

### O que é TailwindCSS?

TailwindCSS é um framework CSS **utility-first**. Em vez de escrever classes como `.card` ou `.btn-primary` e definir o CSS separadamente, você aplica classes utilitárias diretamente no HTML:

```html
<!-- CSS tradicional -->
<button class="btn-primary">Enviar</button>

<!-- TailwindCSS -->
<button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Enviar</button>
```

A vantagem: você nunca sai do HTML para estilizar, e o CSS final contém **apenas** as classes que você usou (tree-shaking automático).

### Como integrar com Django?

Existem duas abordagens:

| Abordagem | Prós | Contras |
|---|---|---|
| **CDN (Play CDN)** | Zero configuração, uma linha no HTML | Não recomendado para produção, arquivo maior |
| **django-tailwind** | Integração nativa com Django, build otimizado | Requer Node.js instalado |

Vamos usar o **`django-tailwind`** — é a abordagem correta para um projeto real.

---

### 5.1 Pré-requisito: Node.js

O TailwindCSS precisa do Node.js para funcionar. Verifique se já está instalado:

```bash
node --version
```

Se não estiver:

**Mac:**

```bash
brew install node
```

**Windows:**

Baixe em [nodejs.org](https://nodejs.org/) e instale a versão LTS.

### 5.2 Instalando o django-tailwind

Com o **venv ativo**:

```bash
pip install django-tailwind
```

Se quiser que o navegador recarregue automaticamente ao salvar alterações (hot reload), instale também:

```bash
pip install 'django-tailwind[reload]'
```

### 5.3 Registrando no settings.py

Adicione ao `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceiros
    'tailwind',
    'django_browser_reload',    # Apenas se instalou o [reload]

    # Apps do projeto
    'core',
]
```

Adicione também a configuração do `NPM_BIN_PATH` (necessário no Windows):

```python
# TailwindCSS
TAILWIND_APP_NAME = 'theme'

# Windows: descomente e ajuste o caminho se necessário
# NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"
```

Se instalou o `django_browser_reload`, adicione o middleware:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',  # Adicione esta linha
]
```

E adicione a URL do reload no `config/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__reload__/', include('django_browser_reload.urls')),  # Adicione esta linha
    path('', include('core.urls')),
]
```

### 5.4 Criando o app de tema

O `django-tailwind` usa um app dedicado para gerenciar os arquivos do Tailwind:

```bash
python manage.py tailwind init
```

Quando perguntar o nome do app, aceite o padrão **`theme`** pressionando Enter.

Registre o app `theme` no `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...

    # Terceiros
    'tailwind',
    'theme',                     # Adicione esta linha
    'django_browser_reload',

    # Apps do projeto
    'core',
]
```

### 5.5 Instalando as dependências do Tailwind

```bash
python manage.py tailwind install
```

Isso executa `npm install` dentro do app `theme` e baixa o TailwindCSS e suas dependências.

### 5.6 Usando o Tailwind nos templates

O app `theme` disponibiliza uma template tag para incluir o CSS. Atualize o `templates/base.html`:

```html
{% load static tailwind_tags %}
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Meu Projeto{% endblock %}</title>
    {% tailwind_css %}
</head>
<body class="bg-gray-50 text-gray-900 min-h-screen flex flex-col">

    <header class="bg-white shadow-sm">
        <nav class="max-w-6xl mx-auto px-4 py-4">
            <a href="{% url 'core:home' %}" class="text-xl font-bold text-blue-600 hover:text-blue-800">
                Meu Projeto
            </a>
        </nav>
    </header>

    <main class="max-w-6xl mx-auto px-4 py-8 flex-1 w-full">
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-white border-t mt-auto">
        <div class="max-w-6xl mx-auto px-4 py-4 text-center text-gray-500 text-sm">
            &copy; 2025 Meu Projeto
        </div>
    </footer>

</body>
</html>
```

### Entendendo as classes do Tailwind

| Classe | O que faz |
|---|---|
| `bg-gray-50` | Fundo cinza claro |
| `text-gray-900` | Texto quase preto |
| `min-h-screen` | Altura mínima = tela inteira |
| `flex flex-col` | Flexbox vertical (header → main → footer) |
| `max-w-6xl mx-auto` | Largura máxima + centralizado |
| `px-4 py-8` | Padding horizontal 1rem, vertical 2rem |
| `shadow-sm` | Sombra sutil |
| `hover:text-blue-800` | Muda cor ao passar o mouse |
| `flex-1` | Ocupa todo espaço disponível (empurra footer para baixo) |
| `mt-auto` | Margem superior automática (cola no fundo) |

### 5.7 Atualize o template da Home

Atualize `core/templates/core/home.html` para usar classes do Tailwind:

```html
{% extends 'base.html' %}

{% block title %}Home{% endblock %}

{% block content %}
<div class="text-center py-20">
    <h1 class="text-4xl font-bold text-gray-800 mb-4">
        Bem-vindo ao Meu Projeto
    </h1>
    <p class="text-lg text-gray-600 mb-8">
        Sistema construído com Django e TailwindCSS.
    </p>
    <a href="{% url 'core:home' %}"
       class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition">
        Começar
    </a>
</div>
{% endblock %}
```

### 5.8 Rodando o servidor com Tailwind

O Tailwind precisa de um processo separado para compilar o CSS em tempo real. Abra **dois terminais**:

**Terminal 1 — Compilador do Tailwind (deve ficar rodando):**

```bash
python manage.py tailwind start
```

**Terminal 2 — Servidor Django:**

```bash
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` e você verá a página Home estilizada.

> **Por que dois terminais?** O `tailwind start` observa seus arquivos HTML e recompila o CSS automaticamente quando você adiciona novas classes. O `runserver` serve a aplicação Django. São processos independentes que precisam rodar simultaneamente.

---

## 6. Configuração de Arquivos Estáticos

Para que imagens, CSS customizado e JavaScript funcionem, configure no `settings.py`:

```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

Crie a pasta:

```bash
mkdir -p static
```

| Variável | O que faz |
|---|---|
| `STATIC_URL` | Prefixo da URL para arquivos estáticos (ex: `/static/imagem.png`) |
| `STATICFILES_DIRS` | Diretórios extras onde o Django procura arquivos estáticos |
| `STATIC_ROOT` | Para onde os estáticos são coletados em produção (`collectstatic`) |

---

## 7. Atualize o `requirements.txt`

```bash
pip freeze > requirements.txt
```

---

## Resumo do Fluxo Completo

```
1. Criar app           →  python manage.py startapp core
2. Registrar app       →  INSTALLED_APPS += ['core']
3. Criar view          →  core/views.py → def home(request)
4. Criar URLs do app   →  core/urls.py → path('', views.home, name='home')
5. Incluir no projeto  →  config/urls.py → include('core.urls')
6. Configurar DIRS     →  settings.py → TEMPLATES.DIRS
7. Criar base.html     →  templates/base.html
8. Criar template      →  core/templates/core/home.html (extends base.html)
9. Instalar Tailwind   →  django-tailwind + tailwind init + tailwind install
10. Rodar              →  tailwind start (terminal 1) + runserver (terminal 2)
```

---

## Exercício Proposto

1. Crie o app `core` e registre no `settings.py`
2. Crie a view `home` em `core/views.py`
3. Crie `core/urls.py` com a rota para a home
4. Inclua as URLs do `core` no `config/urls.py`
5. Configure `TEMPLATES.DIRS` no `settings.py`
6. Crie `templates/base.html` e `core/templates/core/home.html`
7. Teste acessando `http://127.0.0.1:8000/` — deve mostrar a página sem estilo
8. Instale e configure o `django-tailwind`
9. Aplique classes do Tailwind no `base.html` e `home.html`
10. Rode `tailwind start` e `runserver` e veja o resultado estilizado

---

## Próxima Aula

**Aula 04** — Criando Models, Migrations e o primeiro CRUD com Django Admin.
