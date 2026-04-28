# Aula 05 — Categoria: Model + Admin

## Objetivo

Criar o primeiro model de domínio (`Categoria`), aplicar a migration e gerenciar via Django Admin. **Categoria é global** — todos os usuários enxergam as mesmas categorias e só o staff cria.

---

## 1. Criando o app `categorias`

```bash
python manage.py startapp categorias
```

Registre em `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'core',
    'accounts',
    'categorias',
]
```

---

## 2. O Model

`categorias/models.py`:

```python
from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=80, unique=True)
    cor = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text='Cor em formato hex, ex: #3B82F6',
    )
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.nome
```

| Item | O que faz |
|---|---|
| `CharField(max_length=80)` | Coluna `VARCHAR(80)` no MySQL |
| `unique=True` | Cria índice único — impede duas categorias com o mesmo nome |
| `default='#3B82F6'` | Valor padrão (azul Tailwind) |
| `auto_now_add=True` | Preenche **uma vez** na criação |
| `Meta.ordering` | Ordem padrão das queries |
| `verbose_name_plural` | Como aparece no admin (sem ele viraria "categorias" automático, ainda assim explicitar é boa prática) |
| `__str__` | Representação textual — usada no admin, em selects, em prints |

---

## 3. Migration

```bash
python manage.py makemigrations categorias
python manage.py migrate categorias
```

> **Dica:** rode `python manage.py sqlmigrate categorias 0001` para ver o `CREATE TABLE` que o Django vai mandar pro MySQL.

---

## 4. Admin

`categorias/admin.py`:

```python
from django.contrib import admin

from .models import Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cor', 'criada_em']
    search_fields = ['nome']
```

| Atributo | Função |
|---|---|
| `@admin.register(Categoria)` | Decorator que registra o model com o admin customizado |
| `list_display` | Colunas que aparecem na listagem |
| `search_fields` | Habilita o campo de busca filtrando por esses campos |

---

## 5. Cadastrar dados de teste

```bash
python manage.py runserver
```

Acesse `/admin/`, faça login com o superuser, vá em **Categorias** → **Adicionar**.

Cadastre algumas:
- **Trabalho** — `#EF4444` (vermelho)
- **Estudos** — `#3B82F6` (azul)
- **Casa** — `#10B981` (verde)
- **Pessoal** — `#A855F7` (roxo)

---

## 6. Verificar no MySQL (opcional)

```bash
docker exec -it mysql-tarefas mysql -uroot -proot123 tarefas
```

```sql
DESCRIBE categorias_categoria;
SELECT * FROM categorias_categoria;
EXIT;
```

---

## Onde mora cada regra (preview)

- "Não pode existir categoria com nome duplicado" → **Model** (`unique=True`)
- "Listar em ordem alfabética" → **Model** (`Meta.ordering`)
- "Como aparece no select" → **Model** (`__str__`)
- "Quem pode criar" → **Admin** (apenas staff)

Voltaremos a esse mapeamento na Aula 08.

---

## Exercício

1. Crie o app `categorias` e registre
2. Defina o model `Categoria`
3. Rode `makemigrations` e veja o SQL gerado com `sqlmigrate`
4. Aplique a migration
5. Registre no admin
6. Cadastre 4 categorias pelo admin
7. Confira no MySQL com `SELECT * FROM categorias_categoria;`

---

## Próxima aula

[Aula 06 — Tarefa: Model com FK e choices](aula-06-tarefa-model.md).
