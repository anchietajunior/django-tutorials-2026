# Lista de Tarefas — Django + MySQL + TailwindCSS

Aplicação construída ao longo da trilha de aulas em [`../tutoriais/`](../tutoriais/README.md).

## Aulas

| # | Aula | Entrega |
|---|---|---|
| 01 | [Setup do projeto Django](../tutoriais/aula-01-setup-projeto.md) | Projeto rodando com a página padrão do Django |
| 02 | [MySQL via Docker + `.env`](../tutoriais/aula-02-mysql.md) | Banco conectado ao Django |
| 03 | [TailwindCSS (CDN) + layout base](../tutoriais/aula-03-tailwind-e-layout-base.md) | Home estilizada com navbar |
| 04 | [User customizado + autenticação](../tutoriais/aula-04-autenticacao.md) | Signup, login, logout funcionando |
| 05 | [Categoria — Model + Admin](../tutoriais/aula-05-categoria.md) | Categorias gerenciadas pelo Django Admin |
| 06 | [Tarefa — Model com FK e choices](../tutoriais/aula-06-tarefa-model.md) | Tarefa no admin, vinculada a categoria e usuário |
| 07 | [CRUD de Tarefa para o usuário](../tutoriais/aula-07-crud-tarefa.md) | Usuário logado lista, cria, edita, exclui suas tarefas |
| 08 | [Camadas do Django (revisão prática)](../tutoriais/aula-08-camadas.md) | Mapeamento do código existente em camadas |
| 09 | [Filtros, busca + encerramento](../tutoriais/aula-09-filtros-e-encerramento.md) | Lista filtrada por status/categoria + próximos passos |

## Como rodar

```bash
source venv/bin/activate
python manage.py runserver
```

Pré-requisito: container MySQL ativo (ver [Aula 02](../tutoriais/aula-02-mysql.md)).
