# Aula 03 — TailwindCSS sem Node (CDN ou estático)

## Objetivo

Criar a **primeira página visível** do projeto (rota → view → template) e dar estilo a ela com **TailwindCSS sem instalar Node**.

Vamos por dois caminhos:

- **Caminho A — CDN**: uma única tag `<script>` no HTML, zero configuração. É o que a trilha vai usar a partir da próxima aula.
- **Caminho B — Estático**: baixamos o `tailwind.css` pronto, colocamos na pasta `static/` e o Django serve como qualquer outro arquivo. Serve para entender o que é uma **asset pipeline**.

```
[ navegador ] → [ urls.py ] → [ views.py ] → [ render(template) ] → [ HTML + CSS ]
```

> Nesta aula **não vamos criar app**. Tudo fica nos arquivos que já existem dentro de `config/`. A criação do primeiro app é assunto da [Aula 04](aula-04-autenticacao-e-posts.md).

---

## 1. A view mais simples possível

Em Django, uma **view** é apenas uma função que recebe um pedido (`request`) e devolve uma resposta. Vamos escrever a primeira agora.

Crie `config/views.py` (ainda não existe):

```python
from django.http import HttpResponse


def home(request):
    return HttpResponse('Olá, Django!')
```

| Parte | O que faz |
|---|---|
| `from django.http import HttpResponse` | Importa a classe que representa uma resposta HTTP de texto |
| `def home(request):` | Toda view recebe `request` como primeiro parâmetro — é o objeto que carrega tudo sobre o pedido |
| `return HttpResponse('Olá, Django!')` | Devolve uma resposta com o texto |

---

## 2. Conectar a view a uma URL

A view existe, mas o Django ainda não sabe **quando** chamá-la. Quem decide é o roteador. Em `config/urls.py`:

```python
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
]
```

| Linha | O que faz |
|---|---|
| `from . import views` | Importa o `views.py` que acabamos de criar |
| `path('', views.home, name='home')` | Mapeia a URL raiz (`/`) para a função `home`. O `name='home'` é o apelido que vamos usar em todos os templates daqui pra frente |

Suba o servidor e abra `http://127.0.0.1:8000/`:

```bash
python manage.py runserver
```

Você deve ver **Olá, Django!** em texto puro. Esse é o ciclo inteiro: **request → URL → view → response**. Tudo na trilha é variação disso.

---

## 3. Trocar texto puro por um template HTML

### 3.1 Criar a pasta de templates

Na raiz do projeto:

```bash
mkdir templates
```

### 3.2 Avisar o Django onde procurar templates

Em `config/settings.py`, dentro do bloco `TEMPLATES`, troque:

```python
'DIRS': [],
```

Por:

```python
'DIRS': [BASE_DIR / 'templates'],
```

> `BASE_DIR` é a raiz do projeto (já está definida no topo do `settings.py`).

### 3.3 Criar o template

`templates/home.html`:

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Posts</title>
</head>
<body>
    <h1>Olá, Django!</h1>
    <p>Esta é a página inicial.</p>
</body>
</html>
```

### 3.4 Atualizar a view

`config/views.py`:

```python
from django.shortcuts import render


def home(request):
    return render(request, 'home.html')
```

`render` procura o template nas pastas configuradas, devolve um `HttpResponse` com o HTML pronto.

Recarregue a página: agora há um `<h1>` formatado pelo navegador. Mas continua sem **CSS**. Hora do Tailwind.

---

## 4. Por que CSS dói para iniciantes

Antes de mostrar Tailwind, alinhar expectativas: existem **três formas** de adicionar CSS num projeto:

| Forma | Como funciona | Trade-off |
|---|---|---|
| **CSS escrito à mão** | Você cria `styles.css` e escreve regras (`button { ... }`) | Liberdade total, mas você inventa tudo do zero |
| **Framework via CDN** | Carrega o CSS pronto direto da internet (uma `<script>`/`<link>`) | Zero setup; depende de conexão e baixa o framework inteiro |
| **Pipeline de assets (Node, Vite, webpack)** | Roda um build que processa SCSS, JSX, etc. e gera arquivos otimizados | Caminho de produção; requer Node, configuração e tempo de build |

Tailwind foi feito originalmente para o terceiro caminho (build com Node — o "JIT" gera só as classes que você usa, deixando o arquivo final pequeno). Mas para aprender, o terceiro caminho é uma fonte enorme de fricção: instalar Node, criar `package.json`, configurar `tailwind.config.js`...

**Esta aula salta esse caminho** e usa apenas os dois primeiros.

---

## 5. Caminho A — Tailwind via CDN (Play CDN)

Substitua `templates/home.html`:

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Posts</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-900 min-h-screen">
    <main class="max-w-6xl mx-auto px-4 py-20 text-center">
        <h1 class="text-4xl font-bold text-gray-800 mb-4">
            Bem-vindo ao Posts
        </h1>
        <p class="text-lg text-gray-600">
            Sistema construído com Django, MySQL e TailwindCSS.
        </p>
    </main>
</body>
</html>
```

Recarregue. A página agora tem cores, espaçamento, fonte. Sem instalar nada.

### Como o CDN funciona

`<script src="https://cdn.tailwindcss.com"></script>` baixa um JavaScript que:

1. Lê todas as classes que você usou no HTML.
2. Gera as regras CSS correspondentes na hora.
3. Injeta um `<style>` no `<head>` da página.

### Custos do Play CDN

| Custo | Detalhe |
|---|---|
| **Performance** | Roda no navegador a cada carregamento (alguns ms de overhead) |
| **Tamanho** | Não tem otimização — vem o framework inteiro |
| **Aviso no console** | "should not be used in production" — esperado, significa que está funcionando |
| **Requer internet** | Sem rede, a página fica sem estilo |

Para estudo é o caminho de **menor fricção**. Para produção, o ideal é ou usar o caminho B (tailwind compilado servido como estático) ou subir um build com Node.

---

## 6. Pausa para o conceito: o que é uma "asset pipeline"

**Asset** = qualquer arquivo que o navegador baixa além do HTML: CSS, JS, imagem, fonte.

**Pipeline** = a esteira por onde esses assets passam até chegar no navegador. Em projetos grandes essa esteira pode envolver:

```
[ código fonte ] → [ build (Node, Vite) ] → [ minificação ] → [ pasta pública ] → [ navegador ]
```

Em Django, a pipeline mais simples possível é:

```
[ pasta static/ no projeto ] → [ Django serve em /static/... ] → [ navegador ]
```

**Sem build, sem Node, sem minificação.** Você coloca o arquivo lá, escreve `{% static 'arquivo.css' %}` no template e pronto. É exatamente isso que o Caminho B vai fazer.

> **Por que vale entender isso?** Porque imagens dos posts (Aula 06) e qualquer JS que você venha a escrever vão passar pela mesma pipeline. Aprender com Tailwind é só a desculpa.

---

## 7. Caminho B — Tailwind como arquivo estático

A ideia: baixar o CSS do Tailwind **uma única vez**, salvar dentro do projeto (em `static/`) e fazer o Django servi-lo. Resultado: funciona offline, sem JS, sem aviso no console.

### 7.1 Configurar arquivos estáticos

Em `config/settings.py`, no fim do arquivo:

```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

| Setting | O que faz |
|---|---|
| `STATIC_URL` | Prefixo de URL onde os estáticos são servidos. `STATIC_URL = 'static/'` faz `tailwind.css` virar `/static/css/tailwind.css` no navegador |
| `STATICFILES_DIRS` | **Pastas onde o Django procura** os estáticos durante o desenvolvimento. Vamos colocar nossa pasta `static/` aqui |
| `STATIC_ROOT` | Pasta de **destino** quando rodarmos `collectstatic` para subir em produção. Em dev, ele não é usado — só listamos por completude |

> **Dica de leitura:** `DIRS` (plural) = "onde procurar". `ROOT` (singular) = "para onde coletar". A confusão entre os dois é o tropeço clássico de quem está começando com estáticos no Django.

### 7.2 Criar a pasta e baixar o Tailwind

```bash
mkdir -p static/css
```

Baixe o CSS pronto do Tailwind (versão estável compilada) — você pode usar `curl`:

```bash
curl -L https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css -o static/css/tailwind.css
```

Ou, se preferir, abra a URL no navegador, salve o arquivo como `tailwind.css` e mova para `static/css/`.

> **Por que essa versão antiga (2.2.19)?** Ela tem um build estático **completo** disponível em CDN público pronto para baixar. As versões 3+ do Tailwind dependem do JIT (gerar CSS a partir do que você usa) e **não distribuem** mais um arquivo único. Para esta aula, em que o objetivo é "servir um CSS estático", a versão 2 é o caminho mais limpo. Para projetos sérios, use o build via Node.

A estrutura agora deve ser:

```
app/
├── static/
│   └── css/
│       └── tailwind.css   ← arquivo grande, ~3 MB
```

### 7.3 Usar o estático no template

Substitua `templates/home.html`:

```html
{% load static %}
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Posts</title>
    <link rel="stylesheet" href="{% static 'css/tailwind.css' %}">
</head>
<body class="bg-gray-50 text-gray-900 min-h-screen">
    <main class="max-w-6xl mx-auto px-4 py-20 text-center">
        <h1 class="text-4xl font-bold text-gray-800 mb-4">
            Bem-vindo ao Posts
        </h1>
        <p class="text-lg text-gray-600">
            Servido via arquivo estático local.
        </p>
    </main>
</body>
</html>
```

| Parte | O que faz |
|---|---|
| `{% load static %}` | Carrega a tag `{% static %}` para esse template (precisa vir antes de qualquer uso) |
| `{% static 'css/tailwind.css' %}` | Resolve o caminho dentro da pasta `static/`. Se um dia mudar `STATIC_URL`, todos os templates continuam funcionando |

Recarregue. **Mesmo visual** do Caminho A. A diferença está no que o navegador baixou: agora um `tailwind.css` da sua máquina, não da CDN.

### 7.4 Conferir no DevTools

No navegador, abra **Inspecionar → Network → CSS**. Recarregue a página. Você deve ver `tailwind.css` sendo servido por `127.0.0.1:8000/static/css/tailwind.css` com status 200. Isso é a asset pipeline do Django em ação — sem build, sem Node.

---

## 8. Layout reutilizável: `base.html`

Daqui pra frente vamos ter várias páginas (login, cadastro, lista de posts, detalhe...). Repetir todo o `<html>`, `<head>` e a navbar em cada uma é trabalhoso e perigoso (mudar a navbar exigiria editar 10 arquivos).

A solução é **herança de templates**: criar um `base.html` com a estrutura comum, e cada página estende esse base preenchendo apenas o miolo.

`templates/base.html` (escolha **um** dos `<head>` abaixo conforme o caminho que você adotou):

```html
{% load static %}
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Posts{% endblock %}</title>

    {# Caminho A — CDN: #}
    <script src="https://cdn.tailwindcss.com"></script>

    {# Caminho B — estático (comente o de cima e descomente o de baixo): #}
    {# <link rel="stylesheet" href="{% static 'css/tailwind.css' %}"> #}
</head>
<body class="bg-gray-50 text-gray-900 min-h-screen flex flex-col">

    <header class="bg-white shadow-sm">
        <nav class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
            <a href="{% url 'home' %}" class="text-xl font-bold text-blue-600 hover:text-blue-800">
                Posts
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
            &copy; 2026 Posts
        </div>
    </footer>

</body>
</html>
```

| Tag | Função |
|---|---|
| `{% block title %}...{% endblock %}` | Marca um buraco que páginas filhas podem preencher. O conteúdo entre as tags é o **valor padrão** |
| `{% block content %}{% endblock %}` | Buraco principal — onde cada página coloca seu miolo |
| `{% block nav %}{% endblock %}` | Buraco vazio na navbar — vamos preencher na Aula 04 com links de login/cadastro |
| `{% url 'home' %}` | Resolve o nome `home` (definido no `urls.py`) para a URL real (`/`). **Nunca escreva caminhos na mão** |

Agora reescreva `templates/home.html` para usar a herança:

```html
{% extends 'base.html' %}

{% block title %}Início{% endblock %}

{% block content %}
<div class="text-center py-20">
    <h1 class="text-4xl font-bold text-gray-800 mb-4">
        Bem-vindo ao Posts
    </h1>
    <p class="text-lg text-gray-600 mb-8">
        Sistema construído com Django, MySQL e TailwindCSS.
    </p>
</div>
{% endblock %}
```

Recarregue. Mesmo visual, mas agora com header, footer e estrutura reutilizável. A partir da Aula 04, **toda página nova vai estender este `base.html`**.

---

## 9. Qual caminho a trilha vai usar?

A partir da Aula 04, todos os templates assumem o **Caminho A (CDN)** — porque é uma linha só, funciona em qualquer máquina e não polui o projeto com um arquivo de 3 MB.

Você pode trocar para o Caminho B a qualquer momento: basta mexer no `<head>` do `base.html`. Como tudo passa por lá, **uma alteração só** muda toda a aplicação. É o tipo de poder que o `base.html` te dá.

---

## 10. Estrutura final

```
app/
├── config/
│   ├── settings.py    ← TEMPLATES.DIRS, STATIC_URL, STATICFILES_DIRS, STATIC_ROOT
│   ├── urls.py        ← rota para a home
│   ├── views.py       ← função home(request)
│   ├── asgi.py
│   └── wsgi.py
├── templates/
│   ├── base.html      ← layout reutilizável (com Tailwind no <head>)
│   └── home.html      ← estende base.html
├── static/            ← (opcional) só se você usou o Caminho B
│   └── css/
│       └── tailwind.css
├── venv/
├── .env
└── manage.py
```

Ainda **nenhum app** criado. Isso é o tema da próxima aula.

---

## Exercício

1. Crie `config/views.py` com a função `home` retornando `HttpResponse`.
2. Adicione `path('', views.home, name='home')` em `config/urls.py`.
3. Confirme "Olá, Django!" no navegador, em texto puro.
4. Crie a pasta `templates/`, configure `TEMPLATES.DIRS`, crie `home.html` e troque a view para `render`.
5. **Caminho A**: adicione `<script src="https://cdn.tailwindcss.com"></script>` ao `<head>` e classes Tailwind ao `<body>`.
6. **Caminho B (ao menos uma vez, para entender)**: configure `STATIC_URL`/`STATICFILES_DIRS`, crie `static/css/`, baixe o `tailwind.css`, troque o `<script>` por `<link rel="stylesheet" href="{% static 'css/tailwind.css' %}">`. Conferir no DevTools que o arquivo vem do `localhost`.
7. Crie `templates/base.html` com header, footer e os blocks `title`, `content`, `nav`.
8. Reescreva `home.html` estendendo `base.html`.
9. (Opcional) Volte para o Caminho A no `base.html` — você vai ver que **só 1 linha muda** e a aplicação inteira segue funcionando.

---

## 🔁 Vindo do Rails

| Conceito | Rails | Django |
|---|---|---|
| Onde ficam templates | `app/views/<controller>/<action>.html.erb` | `templates/` global ou `<app>/templates/<app>/` por app |
| Sintaxe de template | ERB (`<%= %>`, `<% %>`) | Django Templates (`{{ }}`, `{% %}`) — minimalista, sem Ruby completo dentro |
| Layout reutilizável | `application.html.erb` + `yield` | `base.html` + `{% block content %}{% endblock %}` |
| Bloco nomeado no layout | `yield :head` + `content_for :head do` | `{% block head %}{% endblock %}` + `{% block head %}...{% endblock %}` |
| Helper de URL | `home_path`, `home_url` | `{% url 'home' %}` (string lookup, não método) |
| Pipeline de assets | Sprockets/Propshaft + `app/assets/` | `static/` + `STATICFILES_DIRS` |
| Tag de asset | `<%= stylesheet_link_tag 'app' %>` | `<link rel="stylesheet" href="{% static 'css/tailwind.css' %}">` |
| Carregar helpers | Automático em todo template | `{% load static %}` no topo de cada template que usa |
| Build para produção | `rails assets:precompile` → `public/assets/` | `python manage.py collectstatic` → `STATIC_ROOT` |
| Dev server serve assets | Sprockets/Propshaft no meio do request | Django serve `STATICFILES_DIRS` automaticamente quando `DEBUG=True` |

> 💎 **Vindo do Rails — `{% load %}` é obrigatório.** Em Rails, helpers como `image_tag`, `form_with` ou `link_to` vêm carregados em todo view automaticamente. No Django, **cada template** que use uma tag não-built-in precisa declarar `{% load static %}`, `{% load humanize %}` etc. no topo. Esquecer dá erro de "tag inválida".

> 💎 **Vindo do Rails — `STATICFILES_DIRS` ≠ `STATIC_ROOT`.** Esses dois confundem mesmo quem é veterano de Rails. O paralelo é:
> - `STATICFILES_DIRS` = "onde o Django **procura** seus assets fonte" — equivalente conceitual de `app/assets/stylesheets/` no Rails.
> - `STATIC_ROOT` = "para onde `collectstatic` **copia** tudo na hora do deploy" — equivalente de `public/assets/` (o destino do `assets:precompile`).
>
> Em dev você usa `DIRS`. Em prod, `ROOT`. Misturar os dois é a primeira pegadinha de quem chega de Rails.

> 💎 **Vindo do Rails — sem JIT/build aqui.** Tailwind moderno (v3+) costuma rodar com Node, igual ao caminho `tailwindcss-rails` ou `cssbundling-rails`. Esta aula propositalmente **não** instala Node — o Caminho A usa CDN e o Caminho B usa o build pronto da v2. Quando você precisar de prod sério, o paralelo Rails é claro: gere o CSS otimizado num passo separado e sirva como estático.

---

## Próxima aula

[Aula 04 — Autenticação + CRUD de Posts](aula-04-autenticacao-e-posts.md). É lá que vamos criar o **primeiro app** do projeto e descobrir por que ele existe.
