# Aula 01 — Criando Projetos com Django (Mac e Windows)

## Onde estamos na arquitetura?


## 3. Ambiente Virtual — O que é e por que usar

### O problema

Imagine que você tem dois projetos:
- **Projeto A** usa Django 4.2
- **Projeto B** usa Django 5.1

Se ambos compartilharem a mesma instalação do Python, as versões vão conflitar. Instalar o Django 5.1 vai sobrescrever o 4.2 e quebrar o Projeto A.

### A solução: ambientes virtuais

Um **ambiente virtual** (virtual environment ou `venv`) é uma cópia isolada do Python para cada projeto. Cada `venv` tem seu próprio diretório de pacotes, então as dependências de um projeto não interferem nas de outro.

```
Sistema Operacional
├── Python Global (não mexemos aqui)
├── Projeto A/
│   └── venv/ → Django 4.2, Pillow 9.0
└── Projeto B/
    └── venv/ → Django 5.1, Pillow 10.0
```

### Criando o ambiente virtual

Navegue até a pasta onde deseja criar o projeto:

**Mac:**

```bash
cd ~/Documents/Dev/meu-projeto
python3 -m venv venv
```

**Windows:**

```bash
cd C:\Users\SeuUsuario\Documents\Dev\meu-projeto
python -m venv venv
```

> **O que esse comando faz?** `python3 -m venv venv` executa o módulo `venv` do Python e cria uma pasta chamada `venv` no diretório atual. Essa pasta contém uma cópia do interpretador Python e um diretório `site-packages` vazio onde os pacotes serão instalados.

### Ativando o ambiente virtual

Após criar, você precisa **ativar** o ambiente virtual. Isso faz com que o terminal passe a usar o Python e o `pip` daquela pasta isolada.

**Mac / Linux:**

```bash
source venv/bin/activate
```

**Windows (Prompt de Comando):**

```bash
venv\Scripts\activate
```

**Windows (PowerShell):**

```bash
venv\Scripts\Activate.ps1
```

> **Possível erro no PowerShell:** se aparecer um erro sobre "execução de scripts desabilitada", execute antes:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
> Isso permite a execução de scripts locais no PowerShell.

### Como saber se o ambiente está ativo?

Quando ativo, o terminal mostra o nome do ambiente entre parênteses antes do prompt:

```bash
(venv) usuario@maquina:~/meu-projeto$
```

### Desativando o ambiente virtual

Quando terminar de trabalhar:

```bash
deactivate
```

---

## 4. Instalando o Django

Com o ambiente virtual **ativo**, instale o Django:

```bash
pip install django
```

Confirme a instalação:

```bash
python -m django --version
```

Deve retornar algo como `5.1.x`.

> **Por que `pip` e não `pip3`?** Quando o `venv` está ativo, os comandos `python` e `pip` já apontam para o Python do ambiente virtual, independentemente do sistema operacional. Não é necessário usar `python3` ou `pip3` dentro do venv.

---

## 5. Criando o Projeto Django

### O comando `startproject`

```bash
django-admin startproject config .
```

Vamos entender cada parte:

| Parte | Significado |
|---|---|
| `django-admin` | Utilitário de linha de comando do Django |
| `startproject` | Comando para criar um novo projeto |
| `config` | Nome do pacote de configuração (muitos tutoriais usam o nome do projeto aqui, mas `config` é mais organizado) |
| `.` (ponto) | Cria os arquivos no diretório **atual**, sem criar uma pasta extra aninhada |

### Estrutura gerada

```
meu-projeto/
├── venv/                # Ambiente virtual (já existia)
├── manage.py            # Utilitário de linha de comando do projeto
└── config/
    ├── __init__.py      # Indica que é um pacote Python
    ├── settings.py      # Todas as configurações do projeto
    ├── urls.py          # Roteamento principal de URLs
    ├── asgi.py          # Entrada para servidores ASGI (async)
    └── wsgi.py          # Entrada para servidores WSGI (deploy)
```

### O que cada arquivo faz

**`manage.py`** — ponto de entrada para todos os comandos administrativos. É um wrapper ao redor do `django-admin` que já sabe qual arquivo de settings usar. Você nunca edita este arquivo.

**`config/settings.py`** — o "cérebro" do projeto. Contém:
- `SECRET_KEY` — chave criptográfica usada internamente (nunca compartilhe)
- `DEBUG` — modo de depuração (True em desenvolvimento, False em produção)
- `INSTALLED_APPS` — lista de apps ativos no projeto
- `DATABASES` — configuração do banco de dados
- `LANGUAGE_CODE` e `TIME_ZONE` — idioma e fuso horário

**`config/urls.py`** — mapa de rotas. Quando uma requisição chega, o Django percorre essa lista de cima para baixo até encontrar a URL correspondente.

**`config/wsgi.py`** e **`config/asgi.py`** — interfaces com o servidor web. Em desenvolvimento não usamos diretamente; são importantes para o deploy.

---

## 6. Configurações Iniciais

Abra o arquivo `config/settings.py` e ajuste:

```python
# Idioma em português do Brasil
LANGUAGE_CODE = 'pt-br'

# Fuso horário de Brasília
TIME_ZONE = 'America/Sao_Paulo'
```

> **Por que configurar isso agora?** O `LANGUAGE_CODE` afeta as mensagens do Django Admin e validações de formulários. O `TIME_ZONE` afeta como datas são armazenadas e exibidas. Configurar desde o início evita problemas com datas inconsistentes.

---

## 7. Rodando o Servidor de Desenvolvimento

```bash
python manage.py runserver
```

Saída esperada:

```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s)...
Run 'python manage.py migrate' to apply them.

Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Abra o navegador e acesse **http://127.0.0.1:8000/**. Você verá a página de boas-vindas do Django com um foguete.

### Sobre o aviso de migrations

O aviso sobre "18 unapplied migrations" é normal. São as migrations dos apps internos do Django (auth, admin, sessions, etc.). Resolveremos na próxima aula com:

```bash
python manage.py migrate
```

### Parando o servidor

- **Mac:** `Control + C`
- **Windows:** `Ctrl + C`

---

## 8. O arquivo `requirements.txt`

Sempre registre as dependências do projeto para que outras pessoas (ou você no futuro) possam reproduzir o ambiente:

```bash
pip freeze > requirements.txt
```

Isso gera um arquivo como:

```
asgiref==3.8.1
Django==5.1.4
sqlparse==0.5.3
```

Para instalar as dependências a partir deste arquivo (em outra máquina, por exemplo):

```bash
pip install -r requirements.txt
```

> **Boa prática:** atualize o `requirements.txt` sempre que instalar um novo pacote. Esse arquivo deve estar no controle de versão (Git). A pasta `venv/` **nunca** deve estar no Git.

---

## 9. O arquivo `.gitignore`

Se for usar Git (e deve), crie um `.gitignore` na raiz do projeto:

```
# Ambiente virtual
venv/

# Arquivos do Python
__pycache__/
*.py[cod]
*.pyc

# Variáveis de ambiente
.env

# Banco de dados SQLite (desenvolvimento)
db.sqlite3

# IDE
.vscode/
.idea/

# Sistema operacional
.DS_Store
Thumbs.db
```

---

## Resumo dos Comandos

### Tabela de referência rápida

| Etapa | Mac | Windows |
|---|---|---|
| Verificar Python | `python3 --version` | `python --version` |
| Criar venv | `python3 -m venv venv` | `python -m venv venv` |
| Ativar venv | `source venv/bin/activate` | `venv\Scripts\activate` |
| Desativar venv | `deactivate` | `deactivate` |
| Instalar Django | `pip install django` | `pip install django` |
| Criar projeto | `django-admin startproject config .` | `django-admin startproject config .` |
| Rodar servidor | `python manage.py runserver` | `python manage.py runserver` |
| Gerar requirements | `pip freeze > requirements.txt` | `pip freeze > requirements.txt` |

---

## Exercício Proposto

1. Instale o Python no seu sistema operacional (caso ainda não tenha)
2. Crie uma pasta para o projeto, entre nela e crie um ambiente virtual
3. Ative o ambiente virtual e instale o Django
4. Crie o projeto com `django-admin startproject config .`
5. Altere o idioma para `pt-br` e o fuso horário para `America/Sao_Paulo`
6. Rode o servidor e acesse `http://127.0.0.1:8000/` no navegador
7. Gere o `requirements.txt`
8. Crie o `.gitignore`

Se tudo funcionou, você verá o foguete do Django no navegador. Parabéns — seu ambiente está pronto para a próxima aula!

---

 # Ativa uma vez
  source venv/bin/activate

  # Agora pode rodar tudo que quiser sem ativar de novo
  python manage.py migrate
  python manage.py runserver
  python manage.py createsuperuser
  python manage.py shell


## Próxima Aula

**Aula 02** — Criando o primeiro App, entendendo Models e o Django Admin.

