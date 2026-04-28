# Aula 03 — TailwindCSS (CDN) e Layout Base

## Objetivo

Criar a primeira página do sistema (home) e estilizar com Tailwind. Para manter o setup simples, vamos usar o **Tailwind via CDN** — uma única tag `<script>` no `<head>` e pronto. Sem Node, sem build, sem terminal extra.

```
URL → View → Template (.html) → HTML estilizado
```

> **Nota:** o CDN (Play CDN) é ótimo para aprender e prototipar. Para produção, o caminho recomendado é instalar o Tailwind via npm e gerar um CSS otimizado. A troca é simples e fica como evolução natural depois — por ora, foco em entregar o sistema.

---

## 1. Criando o app `core`

Em Django, cada **app** é um módulo com responsabilidade sobre um domínio. O app `core` cuida de páginas genéricas (home).

```bash
python manage.py startapp core
```

### Registrar em `INSTALLED_APPS`

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
    'core',
]
```

> **Por que registrar?** O Django só descobre migrations, templates e estáticos de apps registrados.

---

## 2. View, URL e template da home

### 2.1 View

`core/views.py`:

```python
from django.shortcuts import render


def home(request):
    return render(request, 'core/home.html')
```

| Linha | O que faz |
|---|---|
| `render(request, 'core/home.html')` | Encontra o template, renderiza e devolve `HttpResponse` |

### 2.2 URLs do app

Crie `core/urls.py` (não vem por padrão):

```python
from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
]
```

| Detalhe | Função |
|---|---|
| `app_name = 'core'` | Namespace — referencia como `core:home` |
| `name='home'` | Identificador que usamos em `{% url %}` (nunca hardcode caminhos) |

### 2.3 Incluir no roteador raiz

`config/urls.py`:

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
```

---

## 3. Templates

### 3.1 Configurar `TEMPLATES.DIRS`

Em `config/settings.py`, dentro de `TEMPLATES`:

```python
'DIRS': [BASE_DIR / 'templates'],
```

> `DIRS` busca templates globais (como `base.html`); `APP_DIRS=True` busca dentro de cada app (`core/templates/...`).

### 3.2 Estrutura

```
app/
├── templates/
│   └── base.html
└── core/
    └── templates/
        └── core/
            └── home.html
```

> **Por que `core/templates/core/`?** Convenção: a subpasta com nome do app evita conflito quando dois apps têm template de mesmo nome.

```bash
mkdir -p templates
mkdir -p core/templates/core
mkdir -p static
```

---

## 4. Tailwind via CDN

Não precisa instalar nada. A linha mágica é uma tag `<script>` no `<head>` do `base.html`:

```html
<script src="https://cdn.tailwindcss.com"></script>
```

Esse script baixa o Tailwind no navegador e gera as classes que você usar no HTML, em tempo real. Resultado: **todas as classes utilitárias do Tailwind disponíveis sem build**.

> **Custos do CDN:** o Tailwind é processado no navegador (alguns segundos de overhead) e não há tree-shaking — o bundle vem inteiro. Em produção, troca-se pelo build com PostCSS. Para aprender, é o caminho de menor fricção.

---

## 5. Template base

`templates/base.html`:

```html
{% load static %}
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Lista de Tarefas{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-900 min-h-screen flex flex-col">

    <header class="bg-white shadow-sm">
        <nav class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
            <a href="{% url 'core:home' %}" class="text-xl font-bold text-blue-600 hover:text-blue-800">
                Lista de Tarefas
            </a>
            <div class="flex items-center gap-4 text-sm">
                {% block nav %}{% endblock %}
            </div>
        </nav>
    </header>

    <main class="max-w-6xl mx-auto px-4 py-8 flex-1 w-full">
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-white border-t mt-auto">
        <div class="max-w-6xl mx-auto px-4 py-4 text-center text-gray-500 text-sm">
            &copy; 2025 Lista de Tarefas
        </div>
    </footer>

</body>
</html>
```

**Pontos chave:**
- `<script src="https://cdn.tailwindcss.com"></script>` — habilita o Tailwind
- `{% block nav %}` será preenchido nas próximas aulas (logado vs deslogado)
- Vamos voltar a esse `base.html` para acrescentar coisas conforme a necessidade aparecer (links da navbar na Aula 04, bloco de mensagens flash na Aula 07)

`core/templates/core/home.html`:

```html
{% extends 'base.html' %}

{% block title %}Início{% endblock %}

{% block content %}
<div class="text-center py-20">
    <h1 class="text-4xl font-bold text-gray-800 mb-4">
        Bem-vindo à Lista de Tarefas
    </h1>
    <p class="text-lg text-gray-600 mb-8">
        Sistema construído com Django, MySQL e TailwindCSS.
    </p>
</div>
{% endblock %}
```

---

## 6. Arquivos estáticos no settings

Mesmo usando o Tailwind via CDN, ainda vamos querer servir CSS/JS/imagens próprias mais para frente. Configure já:

```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

---

## 7. Rodando

Um único processo:

```bash
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` — página estilizada com a navbar (ainda sem links de login, eles entram na próxima aula).

> **Aviso no console do navegador:** o Play CDN imprime um aviso de "should not be used in production". É esperado — significa que está funcionando.

---

## Exercício

1. Crie o app `core` e registre no `settings.py`
2. View `home`, `core/urls.py`, `include` em `config/urls.py`
3. Configure `TEMPLATES.DIRS`
4. Crie `base.html` com o `<script>` do Tailwind via CDN
5. Crie `core/templates/core/home.html` estendendo o `base.html`
6. Configure `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT`
7. Rode `runserver` e veja a home estilizada

---

## Próxima aula

[Aula 04 — User customizado + autenticação](aula-04-autenticacao.md).
