# Aula 02 — Configurando o MySQL no Django

## Onde estamos na arquitetura?

Na Aula 01, criamos o projeto Django e ele veio configurado com **SQLite** — um banco de dados em arquivo, sem necessidade de instalação. Agora vamos trocar para o **MySQL**, um banco de dados relacional completo, usado em produção por milhares de aplicações.

```
[ Projeto criado (Aula 01) ] → [ Instalar MySQL ] → [ Instalar conector ] → [ Configurar settings ] → [ Migrar ]
```

> **Por que trocar?** O SQLite é ótimo para prototipação, mas tem limitações: não suporta acesso concorrente robusto, não tem controle de usuários e não é recomendado para produção com múltiplos acessos simultâneos. O MySQL resolve tudo isso.

---

## 1. Instalando o MySQL

### Mac (via Homebrew)

```bash
brew install mysql
```

Após a instalação, inicie o serviço:

```bash
brew services start mysql
```

Defina a senha do usuário root:

```bash
mysql_secure_installation
```

O assistente vai perguntar:
- **Validate password component?** — `No` (para desenvolvimento, simplifica)
- **New password** — defina uma senha (ex: `root123` para desenvolvimento)
- **Remove anonymous users?** — `Yes`
- **Disallow root login remotely?** — `Yes`
- **Remove test database?** — `Yes`
- **Reload privilege tables?** — `Yes`

### Windows

1. Acesse [dev.mysql.com/downloads/installer](https://dev.mysql.com/downloads/installer/)
2. Baixe o **MySQL Installer** (versão completa ou web)
3. Execute o instalador e escolha **"Developer Default"**
4. Na etapa de configuração:
   - Tipo de servidor: **Development Computer**
   - Porta: **3306** (padrão)
   - Defina a senha do root (ex: `root123` para desenvolvimento)
5. Conclua a instalação

Para verificar se está rodando, abra o Prompt de Comando:

```bash
mysql --version
```

> **Dica Windows:** se o comando `mysql` não for encontrado, adicione o caminho ao PATH. Normalmente fica em `C:\Program Files\MySQL\MySQL Server 8.0\bin`.

---

## 2. Criando o Banco de Dados

Acesse o console do MySQL:

```bash
mysql -u root -p
```

Digite a senha que definiu na instalação. Agora crie o banco de dados:

```sql
CREATE DATABASE meu_projeto CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Verifique se foi criado:

```sql
SHOW DATABASES;
```

Saia do console:

```sql
EXIT;
```

### Por que `utf8mb4`?

O `utf8` do MySQL antigo suporta apenas 3 bytes por caractere, o que exclui emojis e alguns caracteres especiais. O `utf8mb4` suporta 4 bytes — é o UTF-8 completo. Sempre use `utf8mb4`.

---

## 3. Instalando o Conector Python

O Django não conversa diretamente com o MySQL. Ele precisa de um **conector** — uma biblioteca Python que faz a ponte entre o ORM do Django e o MySQL.

Com o **venv ativo**:

```bash
pip install mysqlclient
```

### Possíveis erros na instalação

**Mac — erro de compilação:**

Se der erro ao instalar o `mysqlclient`, instale as dependências de compilação:

```bash
brew install mysql-client pkg-config
export PKG_CONFIG_PATH="$(brew --prefix mysql-client)/lib/pkgconfig"
pip install mysqlclient
```

**Windows — erro de compilação:**

No Windows, o `mysqlclient` pode exigir o Visual C++ Build Tools. Uma alternativa é usar um wheel pré-compilado:

1. Acesse [pypi.org/project/mysqlclient](https://pypi.org/project/mysqlclient/#files)
2. Baixe o `.whl` correspondente à sua versão do Python
3. Instale com `pip install nome_do_arquivo.whl`

**Alternativa para ambos os sistemas:**

Se o `mysqlclient` continuar dando problema, use o `PyMySQL` como fallback:

```bash
pip install pymysql
```

E adicione no `config/__init__.py`:

```python
import pymysql
pymysql.install_as_MySQLdb()
```

> **`mysqlclient` vs `PyMySQL`:** o `mysqlclient` é escrito em C e é mais rápido. O `PyMySQL` é Python puro e mais fácil de instalar. Para projetos em produção, prefira o `mysqlclient`. Para estudos, ambos funcionam.

---

## 4. Variáveis de Ambiente

Antes de configurar o Django, vamos proteger dados sensíveis (senha do banco, SECRET_KEY) usando variáveis de ambiente. **Nunca coloque senhas diretamente no código.**

Instale o `python-decouple`:

```bash
pip install python-decouple
```

Crie um arquivo `.env` na **raiz do projeto** (mesmo nível do `manage.py`):

```env
SECRET_KEY=django-insecure-sua-chave-aqui
DEBUG=True
DB_NAME=meu_projeto
DB_USER=root
DB_PASSWORD=root123
DB_HOST=localhost
DB_PORT=3306
```

> **Importante:** o `.env` já está no `.gitignore` que criamos na Aula 01. Nunca versione este arquivo. Cada desenvolvedor e cada ambiente (dev, staging, prod) terá seu próprio `.env`.

---

## 5. Configurando o `settings.py`

Abra o `config/settings.py` e faça as alterações:

### 5.1 Importar o decouple no topo do arquivo

```python
from decouple import config
```

### 5.2 Substituir a SECRET_KEY

**Antes:**

```python
SECRET_KEY = 'django-insecure-sua-chave-gerada-automaticamente'
```

**Depois:**

```python
SECRET_KEY = config('SECRET_KEY')
```

### 5.3 Configurar o DEBUG

**Antes:**

```python
DEBUG = True
```

**Depois:**

```python
DEBUG = config('DEBUG', default=False, cast=bool)
```

### 5.4 Configurar o banco de dados

**Antes (SQLite padrão):**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Depois (MySQL):**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}
```

### O que cada campo significa

| Campo | Descrição |
|---|---|
| `ENGINE` | Driver do banco. Muda conforme o banco (sqlite3, mysql, postgresql) |
| `NAME` | Nome do banco de dados criado no MySQL |
| `USER` | Usuário do MySQL |
| `PASSWORD` | Senha do usuário |
| `HOST` | Endereço do servidor (localhost para máquina local) |
| `PORT` | Porta do MySQL (padrão: 3306) |
| `OPTIONS.charset` | Garante que a conexão use utf8mb4 |

---

## 6. Aplicando as Migrations

Agora que o Django está apontando para o MySQL, aplique as migrations para criar as tabelas iniciais:

```bash
python manage.py migrate
```

Saída esperada:

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  ...
  Applying sessions.0001_initial... OK
```

> **O que aconteceu?** O Django criou no MySQL todas as tabelas necessárias para o sistema de autenticação (`auth_user`, `auth_group`, etc.), o admin (`django_admin_log`) e o controle de sessões (`django_session`). São as tabelas internas que o framework precisa para funcionar.

### Verificando no MySQL

Você pode confirmar que as tabelas foram criadas:

```bash
mysql -u root -p meu_projeto
```

```sql
SHOW TABLES;
```

Deve listar as tabelas como `auth_user`, `django_admin_log`, `django_session`, etc.

---

## 7. Criando o Superusuário

Com o banco configurado, crie o usuário administrador:

```bash
python manage.py createsuperuser
```

O Django vai pedir:
- **Usuário:** (ex: `admin`)
- **Email:** (ex: `admin@email.com`)
- **Senha:** (mínimo 8 caracteres; em desenvolvimento pode ignorar o aviso de senha fraca digitando `y`)

### Testando o Admin

Rode o servidor e acesse o painel administrativo:

```bash
python manage.py runserver
```

Abra no navegador: **http://127.0.0.1:8000/admin/**

Faça login com o superusuário criado. Se a tela do Admin aparecer em português, tudo está funcionando — o `LANGUAGE_CODE = 'pt-br'` da Aula 01 está ativo.

---

## 8. Atualize o `requirements.txt`

Instalamos novos pacotes, então atualize:

```bash
pip freeze > requirements.txt
```

O arquivo agora deve conter:

```
asgiref==3.8.1
Django==5.1.4
mysqlclient==2.2.6
python-decouple==3.8
sqlparse==0.5.3
```

---

## Resumo dos Comandos

| Etapa | Comando |
|---|---|
| Instalar MySQL (Mac) | `brew install mysql` |
| Iniciar MySQL (Mac) | `brew services start mysql` |
| Acessar console MySQL | `mysql -u root -p` |
| Criar banco | `CREATE DATABASE meu_projeto CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;` |
| Instalar conector | `pip install mysqlclient` |
| Instalar decouple | `pip install python-decouple` |
| Aplicar migrations | `python manage.py migrate` |
| Criar superusuário | `python manage.py createsuperuser` |
| Atualizar requirements | `pip freeze > requirements.txt` |

---

## Exercício Proposto

1. Instale o MySQL no seu sistema operacional
2. Crie o banco de dados `meu_projeto` com charset `utf8mb4`
3. Instale o `mysqlclient` e o `python-decouple`
4. Crie o arquivo `.env` com as credenciais do banco
5. Altere o `settings.py` para usar MySQL e variáveis de ambiente
6. Rode `python manage.py migrate` e verifique as tabelas no MySQL
7. Crie o superusuário e acesse o Django Admin
8. Atualize o `requirements.txt`

---

## Próxima Aula

**Aula 03** — Criando a página Home e adicionando TailwindCSS ao projeto.
