# Aula 01 — Setup do Projeto Django

## Objetivo

Sair do nada e ter um projeto Django rodando localmente.

```
[ Pasta vazia ] → [ venv ] → [ Django ] → [ startproject ] → [ runserver ]
```

---

## 1. Por que ambiente virtual

Cada projeto Python tem suas próprias versões de bibliotecas. Sem isolamento, instalar Django 6 num projeto sobrescreve o Django 4 de outro. O **venv** resolve: cria uma cópia local do Python para o projeto.

```
Sistema → Python global (não mexemos)
└── projeto-A/venv → Django 4.2
└── projeto-B/venv → Django 6.0
```

---

## 2. Criando o projeto

A pasta raiz pode ter qualquer nome. Vamos chamar de `app/` para evitar conflito com o app Django `tarefas` que criaremos depois.

**Mac / Linux:**

```bash
mkdir -p ~/Documents/Dev/lista-tarefas/app
cd ~/Documents/Dev/lista-tarefas/app
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**

```powershell
mkdir C:\Users\SeuUsuario\Documents\Dev\lista-tarefas\app
cd C:\Users\SeuUsuario\Documents\Dev\lista-tarefas\app
python -m venv venv
venv\Scripts\Activate.ps1
```

> **Erro de scripts no PowerShell?** Rode antes:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

Quando o venv está ativo, o terminal mostra `(venv)` antes do prompt:

```
(venv) usuario@maquina:~/Documents/Dev/lista-tarefas/app$
```

Para sair: `deactivate`.

---

## 3. Instalando Django

```bash
pip install django
python -m django --version
```

> **Por que `pip` e não `pip3`?** Quando o `venv` está ativo, `python` e `pip` já apontam para o Python isolado.

---

## 4. Criando o projeto

```bash
django-admin startproject config .
```

| Parte | Significado |
|---|---|
| `django-admin` | CLI que vem com o Django |
| `startproject` | Cria um novo projeto |
| `config` | Nome do pacote de configuração (em vez do nome do projeto, usamos `config` por convenção) |
| `.` | Cria os arquivos no diretório **atual**, sem criar pasta extra aninhada |

### Estrutura gerada

```
app/
├── venv/
├── manage.py
└── config/
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    ├── asgi.py
    └── wsgi.py
```

**`manage.py`** — wrapper do `django-admin` que sabe qual `settings.py` usar. Você nunca edita.

**`config/settings.py`** — o cérebro: `SECRET_KEY`, `DEBUG`, `INSTALLED_APPS`, `DATABASES`, idioma, fuso.

**`config/urls.py`** — roteador raiz. Toda requisição passa por aqui.

**`wsgi.py` / `asgi.py`** — interfaces com servidores web em produção. Em dev não tocamos.

---

## 5. Configurações iniciais

Em `config/settings.py`:

```python
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
```

> Configurar agora evita inconsistências de datas e mensagens no admin depois.

---

## 6. Rodando o servidor

```bash
python manage.py runserver
```

Saída esperada:

```
Watching for file changes with StatReloader
...
You have 18 unapplied migration(s)...

Starting development server at http://127.0.0.1:8000/
```

Acesse `http://127.0.0.1:8000/` — você verá o foguete do Django.

> **O aviso de "18 unapplied migrations"** é normal. São tabelas internas (auth, admin, sessions). Resolveremos na próxima aula, depois de configurar o MySQL.

Para parar: `Ctrl + C`.

---

## 7. `.gitignore`

Crie na raiz (`app/.gitignore`):

```
# Ambiente virtual
venv/

# Python
__pycache__/
*.py[cod]
*.pyc

# Variáveis de ambiente
.env

# Banco local
db.sqlite3

# IDE
.vscode/
.idea/

# SO
.DS_Store
Thumbs.db

# Estáticos coletados
staticfiles/
```

---

## Ritual de cada sessão

```bash
cd ~/Documents/Dev/lista-tarefas/app
source venv/bin/activate          # Mac/Linux
# venv\Scripts\activate           # Windows
python manage.py runserver
```

---

## Exercício

1. Crie a pasta `app/` e entre nela
2. Crie e ative o venv
3. Instale o Django
4. `django-admin startproject config .`
5. Configure `LANGUAGE_CODE` e `TIME_ZONE`
6. Rode `runserver` e veja o foguete
7. Crie o `.gitignore`
8. (Opcional) `git init` e primeiro commit

---

## Próxima aula

[Aula 02 — MySQL via Docker](aula-02-mysql.md).
