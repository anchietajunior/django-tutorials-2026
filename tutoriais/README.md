# Trilha — Posts com Django + MySQL + TailwindCSS

Trilha **enxuta e prática** para construir, do zero ao funcional, um sistema web de **Posts pessoais** usando Django, MySQL e TailwindCSS. Aulas curtas, foco em "aprender fazendo".

## O que vamos construir

Sistema multiusuário onde cada pessoa cria seus **posts** (título, descrição, status), anexa uma **imagem** opcional, **baixa o post como PDF** e gera **explicações automáticas via LLM**. Cada usuário só enxerga os próprios posts.

### Domínio

```
Usuário (1) ───< (N) Post
                     ├── titulo
                     ├── descricao
                     ├── status: em progresso | finalizado
                     └── imagem (opcional)
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
| Upload | `Pillow` + `ImageField` |
| PDF | `WeasyPrint` (HTML+CSS → PDF) |
| LLM | `groq` (Llama 3.1, free tier sem cartão) |

## Pré-requisitos

- Python 3.11+
- MySQL 8 instalado na máquina (instruções na [Aula 02](aula-02-mysql.md))
- Git e um editor de código

## Aulas

| # | Aula | Entrega |
|---|---|---|
| 01 | [Setup do projeto Django](aula-01-setup-projeto.md) | Projeto rodando com a página padrão do Django |
| 02 | [MySQL nativo + `.env`](aula-02-mysql.md) | Banco conectado ao Django |
| 03 | [TailwindCSS sem Node (CDN ou estático)](aula-03-tailwind-sem-node.md) | Primeira página estilizada + entender a asset pipeline |
| 04 | [Autenticação + CRUD de Posts](aula-04-autenticacao-e-posts.md) | Signup/login/logout e CRUD básico de posts |
| 05 | [Controle de acesso (cada um vê só os seus)](aula-05-controle-de-acesso.md) | Posts pertencem a um autor; usuário só vê os próprios |
| 06 | [Regras de negócio: onde colocar?](aula-06-regras-de-negocio.md) | Hierarquia model → manager → services + refator concreto |
| 07 | [Upload de imagem no post](aula-07-upload-de-imagem.md) | Cada post pode ter uma imagem anexada |
| 08 | [Geração de PDF do post](aula-08-pdf.md) | Botão "Baixar PDF" com título, imagem e descrição (via `services.py`) |
| 09 | ["Explicar com IA" (LLM gratuita)](aula-09-explicacao-com-ia.md) | Botão chama Groq/Llama, salva resposta no campo `ai_explanation` |

## Como usar a trilha

1. Faça as aulas em ordem — cada uma depende da anterior
2. Não pule os exercícios no final de cada aula
3. Cada aula é uma sessão de 1h–2h
4. Sempre que abrir o terminal, ative o `venv` antes de qualquer comando

---

Próxima parada: [Aula 01 — Setup do projeto](aula-01-setup-projeto.md).
