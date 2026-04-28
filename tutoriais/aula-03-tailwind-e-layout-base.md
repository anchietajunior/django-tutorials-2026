# Aula 03 — Primeira página: rota, view e template

## Objetivo

Criar a primeira página do sistema. Vamos começar **ridiculamente simples**: uma URL, uma função Python que responde, e um pedacinho de HTML. Só depois adicionamos template e estilo.

```
[ Navegador pede / ]  →  [ urls.py ]  →  [ views.py ]  →  [ HTML de volta ]
```

Não vamos criar nenhum app novo nesta aula. Tudo fica nos arquivos que já existem dentro de `config/`.

> **O que é um "app" no Django?** É um pacote Python que agrupa coisas relacionadas a um assunto (model, views, templates, URLs). A gente vai criar o primeiro app só na **Aula 04**, quando tivermos vários arquivos sobre autenticação para organizar. Para uma única página de boas-vindas, **não precisamos disso**.

---

## 1. A view mais simples possível

Em Django, uma **view** é apenas uma função que recebe um pedido (`request`) e devolve uma resposta (`response`). Vamos escrever a primeira agora.

Crie o arquivo `config/views.py` (ele ainda não existe):

```python
from django.http import HttpResponse


def home(request):
    return HttpResponse('Olá, Django!')
```

| Parte | O que faz |
|---|---|
| `from django.http import HttpResponse` | Importa a classe que representa uma resposta HTTP de texto simples |
| `def home(request):` | Define a função. **Toda view recebe `request` como primeiro parâmetro** — é o objeto que carrega tudo sobre o pedido (URL, método, dados) |
| `return HttpResponse('Olá, Django!')` | Devolve uma resposta com o texto "Olá, Django!" |

Só isso. Uma função Python normal que devolve um objeto.

---

## 2. Conectar a view a uma URL

A view existe, mas o Django ainda não sabe **quando** chamá-la. Quem decide é o roteador de URLs. Abra `config/urls.py` (esse arquivo já foi criado pelo `startproject`):

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
| `from . import views` | Importa o `views.py` que acabamos de criar (o `.` significa "do pacote atual", ou seja, `config/`) |
| `path('', views.home, name='home')` | Mapeia a URL raiz (string vazia = `/`) para a função `home`. O `name='home'` é um apelido que vamos usar nos templates |

> **Por que `name='home'`?** Para nunca mais escrever `/` na mão. Em qualquer lugar do projeto vamos referenciar essa URL como `'home'` — se um dia mudarmos o caminho, só ajustamos aqui.

---

## 3. Testar

```bash
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`. Deve aparecer **Olá, Django!** em texto puro, sem estilização.

Pare o servidor com `Ctrl + C`.

> Cabe parar e celebrar: você acabou de fazer **request → URL → view → response**. Esse é o ciclo inteiro do Django. Tudo daqui pra frente é variação em cima disso.

---

## 4. Trocar texto puro por um template HTML

Texto cru é feio. Vamos devolver um arquivo HTML. Para isso, dois passos:

### 4.1 Criar a pasta de templates

Na raiz do projeto:

```bash
mkdir templates
```

### 4.2 Avisar o Django onde procurar templates

Em `config/settings.py`, dentro do bloco `TEMPLATES`, troque:

```python
'DIRS': [],
```

Por:

```python
'DIRS': [BASE_DIR / 'templates'],
```

> `DIRS` é a lista de pastas globais de templates. `BASE_DIR` é a raiz do projeto (já definida no topo do `settings.py`).

### 4.3 Criar o template

`templates/home.html`:

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Lista de Tarefas</title>
</head>
<body>
    <h1>Olá, Django!</h1>
    <p>Esta é a página inicial.</p>
</body>
</html>
```

### 4.4 Atualizar a view para renderizar o template

Em `config/views.py`:

```python
from django.shortcuts import render


def home(request):
    return render(request, 'home.html')
```

| Mudança | O que faz |
|---|---|
| `render(request, 'home.html')` | Procura `home.html` nas pastas configuradas, renderiza e devolve um `HttpResponse` com o HTML |

Recarregue a página. Agora aparece um `<h1>` formatado.

---

## 5. Estilizar com TailwindCSS via CDN

HTML sem estilo segue feio. Em vez de instalar Node + build de CSS, vamos usar o **Tailwind via CDN**: uma única tag `<script>` no `<head>` e todas as classes utilitárias do Tailwind ficam disponíveis.

> **Custos do CDN:** o Tailwind é processado no navegador (alguns segundos de overhead) e o bundle vem inteiro (sem otimização). Em produção, o caminho recomendado é instalar via npm e gerar um CSS otimizado. Para aprender, é o caminho de menor fricção.

Substitua `templates/home.html` por:

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Lista de Tarefas</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-900 min-h-screen flex flex-col">
    <main class="max-w-6xl mx-auto px-4 py-20 text-center">
        <h1 class="text-4xl font-bold text-gray-800 mb-4">
            Bem-vindo à Lista de Tarefas
        </h1>
        <p class="text-lg text-gray-600">
            Sistema construído com Django, MySQL e TailwindCSS.
        </p>
    </main>
</body>
</html>
```

Recarregue. Agora a página tem estilo.

> **Aviso no console do navegador:** o CDN imprime um aviso de "should not be used in production". É esperado — significa que está funcionando.

---

## 6. Layout reutilizável: `base.html`

Daqui pra frente vamos ter várias páginas (login, lista de tarefas, detalhe...). Repetir todo o `<html>`, `<head>` e header em cada uma é trabalhoso e perigoso (mudar a navbar exigiria editar 10 arquivos).

A solução do Django é **herança de templates**: criar um `base.html` com a estrutura comum, e cada página estende esse base preenchendo apenas o miolo.

`templates/base.html`:

```html
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
            <a href="{% url 'home' %}" class="text-xl font-bold text-blue-600 hover:text-blue-800">
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

| Tag | Função |
|---|---|
| `{% block title %}...{% endblock %}` | Marca um buraco que páginas filhas podem preencher. O conteúdo entre as tags é o **valor padrão** (se a filha não preencher, esse texto vai pra tela) |
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
        Bem-vindo à Lista de Tarefas
    </h1>
    <p class="text-lg text-gray-600 mb-8">
        Sistema construído com Django, MySQL e TailwindCSS.
    </p>
</div>
{% endblock %}
```

| Tag | Função |
|---|---|
| `{% extends 'base.html' %}` | Diz "minha estrutura é a do `base.html`" |
| `{% block title %}Início{% endblock %}` | Preenche o buraco do título |
| `{% block content %}...{% endblock %}` | Preenche o buraco principal |

Recarregue. Mesmo visual, mas agora com header, footer e estrutura reutilizável.

---

## 7. Arquivos estáticos no settings

Mais para frente vamos querer servir CSS/JS/imagens próprios. Já deixe configurado em `config/settings.py`:

```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

E crie a pasta vazia:

```bash
mkdir static
```

| Setting | Função |
|---|---|
| `STATIC_URL` | Prefixo da URL onde os arquivos estáticos serão servidos |
| `STATICFILES_DIRS` | Pastas onde o Django procura estáticos durante o desenvolvimento |
| `STATIC_ROOT` | Pasta para onde os estáticos vão ser **coletados** quando subirmos pra produção (ainda não usamos) |

---

## Estrutura final do projeto

```
app/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py        ← novo (uma única função, "home")
│   ├── asgi.py
│   └── wsgi.py
├── templates/
│   ├── base.html       ← novo (layout reutilizável)
│   └── home.html       ← novo (estende o base)
├── static/             ← novo (vazio por enquanto)
├── venv/
├── .env
├── .gitignore
└── manage.py
```

Ainda **nenhum** app criado. Isso vem na Aula 04.

---

## Exercício

1. Crie `config/views.py` com a função `home` retornando `HttpResponse`
2. Adicione a rota `path('', views.home, name='home')` em `config/urls.py`
3. Rode o servidor e veja "Olá, Django!" em texto puro
4. Crie a pasta `templates/` e configure `TEMPLATES.DIRS`
5. Crie `templates/home.html` e troque a view para usar `render`
6. Adicione o `<script>` do Tailwind CDN no `home.html`
7. Crie `templates/base.html` com header/footer e blocos `title`, `content`, `nav`
8. Reescreva `home.html` estendendo o `base.html`
9. Configure `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT` e crie a pasta `static/`

---

## Próxima aula

[Aula 04 — User customizado + autenticação](aula-04-autenticacao.md). É lá que vamos criar o **primeiro app** do projeto e descobrir por que ele existe.
