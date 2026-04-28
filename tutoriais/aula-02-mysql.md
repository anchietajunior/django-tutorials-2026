# Aula 02 — MySQL nativo + `.env`

## Objetivo

Trocar o SQLite padrão por MySQL **instalado diretamente na máquina** e isolar credenciais em `.env`.

```
[ MySQL local ] → [ DB tarefas ] → [ Django settings ] → [ migrate ]
```

> **Por que MySQL e não SQLite?** SQLite é ótimo para começar, mas em produção quase sempre usamos um SGBD cliente-servidor. Aprender a configurar a conexão agora é parte do trabalho.

---

## 1. Instalar o MySQL

Escolha o caminho do seu sistema operacional. Em todos eles, no fim você vai ter um servidor MySQL escutando em `localhost:3306`.

### Windows

1. Baixe o **MySQL Installer** em [dev.mysql.com/downloads/installer](https://dev.mysql.com/downloads/installer/)
2. Execute e escolha **Developer Default** (instala servidor + utilitários + connector)
3. Quando pedir, defina a senha do usuário `root` (anote — vai usar no `.env`)
4. Aceite a porta padrão **3306** e finalize

### macOS

```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

`mysql_secure_installation` é interativo: define a senha do `root`, remove usuários anônimos, etc. Anote a senha.

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl enable --now mysql
sudo mysql_secure_installation
```

---

## 2. Criar o database `tarefas`

Conecte como root:

```bash
mysql -u root -p
```

Dentro do prompt do MySQL, crie o database com `utf8mb4` (UTF-8 completo, suporta emojis):

```sql
CREATE DATABASE tarefas
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

SHOW DATABASES;
EXIT;
```

> **Por que `utf8mb4`?** O `utf8` antigo do MySQL suporta apenas 3 bytes — exclui emojis e alguns caracteres asiáticos. `utf8mb4` é o UTF-8 real (4 bytes).

---

## 3. Conector Python: `mysqlclient`

Com o **venv ativo**:

### Windows

Em geral o wheel pré-compilado funciona direto:

```bash
pip install mysqlclient
```

Se falhar, baixe um wheel específico em [pypi.org/project/mysqlclient/#files](https://pypi.org/project/mysqlclient/#files) e instale com `pip install nome_do_arquivo.whl`.

### macOS

```bash
brew install mysql-client pkg-config
export PKG_CONFIG_PATH="$(brew --prefix mysql-client)/lib/pkgconfig"
pip install mysqlclient
```

### Linux (Debian/Ubuntu)

```bash
sudo apt install pkg-config default-libmysqlclient-dev build-essential
pip install mysqlclient
```

> **Por que `mysqlclient` e não outro?** É o driver recomendado pela comunidade Django, escrito em C, mais rápido. Versões recentes do Django (6+) exigem ele para o backend MySQL nativo.

---

## 4. `python-decouple` para variáveis de ambiente

Senhas **nunca** vão pro código. Vamos isolá-las num `.env`.

```bash
pip install python-decouple
```

Crie `app/.env` (raiz do projeto):

```env
SECRET_KEY=django-insecure-troque-isso-em-producao-1234567890
DEBUG=True
DB_NAME=tarefas
DB_USER=root
DB_PASSWORD=sua_senha_do_root_aqui
DB_HOST=127.0.0.1
DB_PORT=3306
```

> O `.env` já está no `.gitignore` da Aula 01. Cada aluno tem o seu — a senha do MySQL local pode (e deve) ser diferente da do colega.

---

## 5. Configurar `settings.py`

### 5.1 Importar o decouple

No topo de `config/settings.py`:

```python
from decouple import config
```

### 5.2 SECRET_KEY e DEBUG

Substitua:

```python
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
```

### 5.3 DATABASES

Substitua o bloco SQLite por:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}
```

| Campo | Descrição |
|---|---|
| `ENGINE` | Driver do banco |
| `NAME` | Database criado no MySQL |
| `HOST` / `PORT` | Onde está o servidor (na sua máquina, `127.0.0.1:3306`) |
| `OPTIONS.charset` | Garante `utf8mb4` na conexão |

---

## 6. Validar conexão

```bash
python manage.py check
```

Deve responder `System check identified no issues (0 silenced).`

Se aparecer erro `Access denied`, revise a senha no `.env`. Se aparecer `Unknown database 'tarefas'`, volte ao passo 2 e crie o database.

> **Por que não rodar `migrate` agora?** Vamos criar o **User customizado** na Aula 04 antes da primeira migration. Adiar o `migrate` evita resetar o banco depois.

---

## Resumo dos comandos

| Etapa | Comando |
|---|---|
| Conectar no MySQL | `mysql -u root -p` |
| Criar database | `CREATE DATABASE tarefas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;` |
| Listar databases | `SHOW DATABASES;` |
| Conector Python | `pip install mysqlclient` |
| Decouple | `pip install python-decouple` |
| Validar | `python manage.py check` |

---

## Exercício

1. Instale o MySQL na sua máquina e defina a senha do `root`
2. Conecte com `mysql -u root -p` e crie o database `tarefas` com `utf8mb4`
3. Instale `mysqlclient` e `python-decouple` no venv
4. Crie o `.env` com as credenciais
5. Ajuste `settings.py` para ler do `.env` e usar MySQL
6. Rode `python manage.py check` — deve passar sem erros

---

## Próxima aula

[Aula 03 — TailwindCSS e layout base](aula-03-tailwind-e-layout-base.md).
