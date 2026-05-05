# Posts — Django + MySQL + TailwindCSS

Aplicação Django construída ao longo de uma trilha de aulas. O código fica em [`app/`](app/) e os tutoriais em [`tutoriais/`](tutoriais/README.md).

## Aulas

| # | Aula | Entrega |
|---|---|---|
| 01 | [Setup do projeto Django](tutoriais/aula-01-setup-projeto.md) | Projeto rodando com a página padrão do Django |
| 02 | [MySQL nativo + `.env`](tutoriais/aula-02-mysql.md) | Banco conectado ao Django |
| 03 | [TailwindCSS sem Node (CDN ou estático)](tutoriais/aula-03-tailwind-sem-node.md) | Primeira página estilizada + entender a asset pipeline |
| 04 | [Autenticação + CRUD de Posts](tutoriais/aula-04-autenticacao-e-posts.md) | Signup/login/logout e CRUD básico de posts |
| 05 | [Controle de acesso (cada um vê só os seus)](tutoriais/aula-05-controle-de-acesso.md) | Posts pertencem a um autor; usuário só vê os próprios |
| 06 | [Regras de negócio: onde colocar?](tutoriais/aula-06-regras-de-negocio.md) | Hierarquia model → manager → services + refator concreto |
| 07 | [Upload de imagem no post](tutoriais/aula-07-upload-de-imagem.md) | Cada post pode ter uma imagem anexada |
| 08 | [Geração de PDF do post](tutoriais/aula-08-pdf.md) | Botão "Baixar PDF" com título, imagem e descrição (via `services.py`) |

## Como rodar

```bash
cd app
source venv/bin/activate
python manage.py runserver
```

Pré-requisito: MySQL rodando localmente com o database criado (ver [Aula 02](tutoriais/aula-02-mysql.md)).
