# Aula 02 — MySQL via Docker

## Objetivo

Trocar o SQLite padrão por MySQL rodando num **container Docker** — sem instalar nada no seu sistema operacional. Isolar credenciais em `.env`.

```
[ Docker MySQL ] → [ DB tarefas ] → [ Django settings ] → [ migrate ]
```

> **Por que Docker?** MySQL nativo exige instalar serviço, configurar senha root, gerenciar versão. Container resolve em uma linha e zero contaminação do sistema.

---

## 1. Subir o container MySQL

Pré-requisito: ter o Docker Desktop instalado e rodando.

```bash
docker run -d \
  --name mysql-tarefas \
  -e MYSQL_ROOT_PASSWORD=root123 \
  -e MYSQL_DATABASE=tarefas \
  -p 3306:3306 \
  mysql:8 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci
```

| Flag | Significado |
|---|---|
| `-d` | Roda em background (detached) |
| `--name` | Nome do container, para referenciar depois |
| `-e MYSQL_ROOT_PASSWORD` | Define a senha do root |
| `-e MYSQL_DATABASE` | Cria o database `tarefas` na inicialização |
| `-p 3306:3306` | Mapeia a porta do container para a máquina |
| `--character-set-server=utf8mb4` | Usa UTF-8 completo (suporta emojis) |
| `--collation-server=utf8mb4_unicode_ci` | Comparação de strings sensível a unicode |

> **Por que `utf8mb4`?** O `utf8` antigo do MySQL suporta apenas 3 bytes — exclui emojis. `utf8mb4` é o UTF-8 real (4 bytes).

### Verificar se subiu

```bash
docker ps
```

Deve listar `mysql-tarefas` com status `Up`.

### Conectar via console (opcional)

```bash
docker exec -it mysql-tarefas mysql -uroot -proot123
```

Dentro do MySQL:

```sql
SHOW DATABASES;
EXIT;
```

### Comandos úteis

```bash
docker stop mysql-tarefas    # parar
docker start mysql-tarefas   # ligar de novo
docker logs mysql-tarefas    # ver logs
docker rm -f mysql-tarefas   # remover (perde os dados)
```

---

## 2. Conector Python: `mysqlclient`

Com o **venv ativo**:

**Mac:**

```bash
brew install mysql-client pkg-config
export PKG_CONFIG_PATH="$(brew --prefix mysql-client)/lib/pkgconfig"
pip install mysqlclient
```

**Linux (Debian/Ubuntu):**

```bash
sudo apt install pkg-config default-libmysqlclient-dev build-essential
pip install mysqlclient
```

**Windows:**

Baixe um wheel pré-compilado em [pypi.org/project/mysqlclient/#files](https://pypi.org/project/mysqlclient/#files) e instale com `pip install nome_do_arquivo.whl`.

> **Por que `mysqlclient` e não outro?** É o driver oficial recomendado pela comunidade Django, em C, mais rápido. Versões recentes do Django (6+) exigem ele.

---

## 3. `python-decouple` para variáveis de ambiente

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
DB_PASSWORD=root123
DB_HOST=127.0.0.1
DB_PORT=3306
```

> O `.env` já está no `.gitignore` da Aula 01. Cada desenvolvedor terá o seu.

---

## 4. Configurar `settings.py`

### 4.1 Importar o decouple

No topo de `config/settings.py`:

```python
from decouple import config
```

### 4.2 SECRET_KEY e DEBUG

Substitua:

```python
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
```

### 4.3 DATABASES

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
| `HOST` / `PORT` | Onde está o servidor (no container, mapeado para 127.0.0.1:3306) |
| `OPTIONS.charset` | Garante `utf8mb4` na conexão |

---

## 5. Validar conexão

```bash
python manage.py check
```

Deve responder `System check identified no issues (0 silenced).`

> **Por que não rodar `migrate` agora?** Vamos criar o **User customizado** na Aula 04 antes da primeira migration. Adiar o `migrate` evita resetar o banco depois.

---

## Resumo dos comandos

| Etapa | Comando |
|---|---|
| Subir MySQL | `docker run -d --name mysql-tarefas -e MYSQL_ROOT_PASSWORD=root123 -e MYSQL_DATABASE=tarefas -p 3306:3306 mysql:8 --character-set-server=utf8mb4` |
| Status | `docker ps` |
| Parar | `docker stop mysql-tarefas` |
| Ligar | `docker start mysql-tarefas` |
| Console | `docker exec -it mysql-tarefas mysql -uroot -proot123` |
| Conector Python | `pip install mysqlclient` (com pkg-config configurado) |
| Validar | `python manage.py check` |

---

## Exercício

1. Suba o container MySQL
2. Confirme com `docker ps`
3. Instale `mysqlclient` e `python-decouple`
4. Crie o `.env` com as credenciais
5. Ajuste `settings.py` para ler do `.env` e usar MySQL
6. Rode `python manage.py check` — deve passar sem erros

---

## Próxima aula

[Aula 03 — TailwindCSS e layout base](aula-03-tailwind-e-layout-base.md).
