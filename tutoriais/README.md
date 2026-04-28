# Trilha — Lista de Tarefas com Django + MySQL + TailwindCSS

Trilha **enxuta e prática** para construir, do zero ao funcional, um sistema web de **Lista de Tarefas** usando Django, MySQL e TailwindCSS. Aulas curtas, foco em "aprender fazendo".

## O que vamos construir

Sistema multiusuário onde cada pessoa cadastra suas próprias tarefas, organizadas por **categoria** (gerenciadas pelo admin) e com **status** (pendente, em andamento, concluída).

### Domínio

```
Usuário (1) ───< (N) Tarefa (N) >─── (1) Categoria
                       │
                       └── status: pendente | em andamento | concluída
```

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.11+ |
| Framework | Django 5.x ou 6.x |
| Banco | MySQL 8 (instalado nativamente na máquina) |
| Frontend | TailwindCSS via CDN (Play CDN — zero build) |
| Configuração | `python-decouple` + `.env` |
| Auth | `django.contrib.auth` com `User` customizado |

## Pré-requisitos

- Python 3.11+
- MySQL 8 instalado na máquina (instruções na [Aula 02](aula-02-mysql.md))
- Git e um editor de código

## Aulas

| # | Aula | Entrega |
|---|---|---|
| 01 | [Setup do projeto Django](aula-01-setup-projeto.md) | Projeto rodando com a página padrão do Django |
| 02 | [MySQL nativo + `.env`](aula-02-mysql.md) | Banco conectado ao Django |
| 03 | [TailwindCSS + layout base](aula-03-tailwind-e-layout-base.md) | Home estilizada com navbar |
| 04 | [User customizado + autenticação](aula-04-autenticacao.md) | Signup, login, logout funcionando |
| 05 | [Categoria — Model + Admin](aula-05-categoria.md) | Categorias gerenciadas pelo Django Admin |
| 06 | [Tarefa — Model com FK e choices](aula-06-tarefa-model.md) | Tarefa no admin, vinculada a categoria e usuário |
| 07 | [CRUD de Tarefa para o usuário](aula-07-crud-tarefa.md) | Usuário logado lista, cria, edita, exclui suas tarefas |
| 08 | [Camadas do Django (revisão prática)](aula-08-camadas.md) | Mapeamento do código existente em camadas |
| 09 | [Filtros, busca + encerramento](aula-09-filtros-e-encerramento.md) | Lista filtrada por status/categoria + próximos passos |

## Como usar a trilha

1. Faça as aulas em ordem — cada uma depende da anterior
2. Não pule os exercícios no final de cada aula
3. Cada aula é uma sessão de 1h–2h
4. Sempre que abrir o terminal, ative o `venv` antes de qualquer comando

---

Próxima parada: [Aula 01 — Setup do projeto](aula-01-setup-projeto.md).
