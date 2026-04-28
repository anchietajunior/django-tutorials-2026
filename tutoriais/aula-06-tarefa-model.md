# Aula 06 — Tarefa: Model com FK, Choices e Admin

## Objetivo

Criar o model `Tarefa` introduzindo três conceitos novos: **`ForeignKey`** (relacionamento), **`TextChoices`** (status como enum) e **sobrescrever `save()`** (regra de domínio sobre um único registro).

---

## 1. Criando o app `tarefas`

```bash
python manage.py startapp tarefas
```

Registre em `INSTALLED_APPS`:

```python
'tarefas',
```

---

## 2. O Model

`tarefas/models.py`:

```python
from django.conf import settings
from django.db import models
from django.utils import timezone


class Tarefa(models.Model):

    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em andamento'
        CONCLUIDA = 'CONCLUIDA', 'Concluída'

    class Prioridade(models.TextChoices):
        BAIXA = 'BAIXA', 'Baixa'
        MEDIA = 'MEDIA', 'Média'
        ALTA = 'ALTA', 'Alta'

    titulo = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
    )
    prioridade = models.CharField(
        max_length=10,
        choices=Prioridade.choices,
        default=Prioridade.MEDIA,
    )
    categoria = models.ForeignKey(
        'categorias.Categoria',
        on_delete=models.PROTECT,
        related_name='tarefas',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tarefas',
    )
    criada_em = models.DateTimeField(auto_now_add=True)
    concluida_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'tarefa'
        verbose_name_plural = 'tarefas'

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if self.status == self.Status.CONCLUIDA and self.concluida_em is None:
            self.concluida_em = timezone.now()
        elif self.status != self.Status.CONCLUIDA:
            self.concluida_em = None
        super().save(*args, **kwargs)
```

### Pontos a entender

#### `TextChoices`

```python
class Status(models.TextChoices):
    PENDENTE = 'PENDENTE', 'Pendente'
```

Define um enum com **valor armazenado** + **label legível**. Vantagens:
- Acessível como `Tarefa.Status.PENDENTE` (o editor autocompleta)
- Em queries: `Tarefa.objects.filter(status=Tarefa.Status.PENDENTE)`
- O Django gera automaticamente `tarefa.get_status_display()` que retorna `'Pendente'`

#### `ForeignKey` e `on_delete`

Cada FK exige decidir o que acontece quando o pai é deletado:

| Opção | Comportamento |
|---|---|
| `CASCADE` | Apaga as tarefas junto com o pai |
| `PROTECT` | Bloqueia deletar o pai se houver filhos |
| `SET_NULL` | Filhos ficam com `NULL` (precisa `null=True`) |

**Decisões aqui:**
- `categoria` → `PROTECT`. Não queremos perder tarefas porque alguém apagou uma categoria
- `usuario` → `CASCADE`. Se o usuário se descadastra, suas tarefas vão junto

> **`'categorias.Categoria'` (string) vs `Categoria` (import)?** A string evita import circular e funciona mesmo se o app `categorias` for carregado depois. Boa prática para FKs entre apps.

> **`settings.AUTH_USER_MODEL`?** Não importamos `User` direto para não acoplar `tarefas` ao app `accounts`. É o padrão recomendado pela documentação.

#### `related_name='tarefas'`

Permite a relação inversa: `usuario.tarefas.all()` ou `categoria.tarefas.all()`.

#### Sobrescrever `save()`

```python
def save(self, *args, **kwargs):
    if self.status == self.Status.CONCLUIDA and self.concluida_em is None:
        self.concluida_em = timezone.now()
    elif self.status != self.Status.CONCLUIDA:
        self.concluida_em = None
    super().save(*args, **kwargs)
```

Regra de **um único registro**: quando o status vira "concluída", carimba a data; quando volta de concluída, limpa. Mora no model porque depende **só do próprio registro**.

> Para regras com efeito colateral (registrar log, enviar e-mail) o lugar não seria `save()`, seria um service. Discussão na Aula 08.

---

## 3. Migration

```bash
python manage.py makemigrations tarefas
python manage.py migrate tarefas
```

Veja a `FOREIGN KEY` no SQL com `python manage.py sqlmigrate tarefas 0001`.

---

## 4. Admin

`tarefas/admin.py`:

```python
from django.contrib import admin

from .models import Tarefa


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'status', 'prioridade', 'categoria', 'criada_em']
    list_filter = ['status', 'prioridade', 'categoria']
    search_fields = ['titulo', 'descricao']
```

| Atributo | Função |
|---|---|
| `list_display` | Colunas da listagem |
| `list_filter` | Sidebar à direita com filtros |
| `search_fields` | Campo de busca |

---

## 5. Cadastrar tarefas de teste

Acesse `/admin/`, vá em **Tarefas** → **Adicionar**. Crie 3-4 tarefas atribuídas ao seu superuser, em categorias diferentes, com status variados (uma `CONCLUIDA` para testar o `save()`).

Confira no shell que o `concluida_em` foi preenchido automaticamente:

```bash
python manage.py shell
```

```python
from tarefas.models import Tarefa
for t in Tarefa.objects.all():
    print(t, t.status, t.concluida_em)
```

---

## 6. Validar `PROTECT`

Tente apagar uma categoria que tem tarefas. O admin vai recusar com **"Não é possível excluir"** — é o `PROTECT` em ação.

---

## Exercício

1. Crie o app `tarefas`
2. Defina o model com FK, `TextChoices` e `save()` sobrescrito
3. Migre e veja o SQL com `sqlmigrate`
4. Registre no admin com `list_display` e `list_filter`
5. Cadastre 4-5 tarefas pelo admin (algumas concluídas)
6. Verifique no shell que `concluida_em` foi preenchido sozinho
7. Tente apagar uma categoria com tarefas → deve falhar

---

## Próxima aula

[Aula 07 — CRUD de Tarefa para o usuário](aula-07-crud-tarefa.md).
