# Aula 09 — Filtros, Busca e Encerramento

## Objetivo

Polir o sistema com **filtros por status e categoria** + **busca por título**, tudo via querystring. Encerrar a trilha apontando próximos passos.

---

## 1. Evoluindo a `TarefaListView`

A view já filtra por usuário. Vamos fazer ela aceitar 3 parâmetros opcionais via GET:

- `?status=PENDENTE`
- `?categoria=3`
- `?q=relatório`

`tarefas/views.py` (substitua a `TarefaListView`):

```python
class TarefaListView(LoginRequiredMixin, ListView):
    model = Tarefa
    template_name = 'tarefas/lista.html'
    context_object_name = 'tarefas'
    paginate_by = 20

    def get_queryset(self):
        qs = Tarefa.objects.filter(usuario=self.request.user).select_related('categoria')

        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)

        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)

        termo = self.request.GET.get('q')
        if termo:
            qs = qs.filter(titulo__icontains=termo)

        return qs

    def get_context_data(self, **kwargs):
        from categorias.models import Categoria

        ctx = super().get_context_data(**kwargs)
        ctx['categorias'] = Categoria.objects.all()
        ctx['statuses'] = Tarefa.Status.choices
        ctx['status_atual'] = self.request.GET.get('status', '')
        ctx['categoria_atual'] = self.request.GET.get('categoria', '')
        ctx['termo_atual'] = self.request.GET.get('q', '')
        return ctx
```

| Detalhe | Função |
|---|---|
| `request.GET.get('status')` | Lê parâmetro da URL (`?status=PENDENTE`) |
| `titulo__icontains` | Busca case-insensitive por substring (`LIKE '%relatório%'` no MySQL) |
| `Tarefa.Status.choices` | Lista de tuplas `(valor, label)` pronta para o `<select>` |
| `get_context_data` | Adiciona dados extras ao contexto — usado pelo template para preencher os selects |

---

## 2. Form de filtros no template

Em `tarefas/templates/tarefas/lista.html`, **logo após o `<h1>` e antes da tabela**, adicione:

```html
<form method="get" class="flex flex-wrap gap-2 mb-6 bg-white p-4 rounded-lg shadow-sm">
    <input type="text" name="q" value="{{ termo_atual }}" placeholder="Buscar pelo título..."
           class="flex-1 min-w-[180px] border border-gray-300 rounded px-3 py-2">

    <select name="status" class="border border-gray-300 rounded px-3 py-2">
        <option value="">Todos os status</option>
        {% for valor, label in statuses %}
            <option value="{{ valor }}" {% if valor == status_atual %}selected{% endif %}>{{ label }}</option>
        {% endfor %}
    </select>

    <select name="categoria" class="border border-gray-300 rounded px-3 py-2">
        <option value="">Todas as categorias</option>
        {% for cat in categorias %}
            <option value="{{ cat.id }}" {% if cat.id|stringformat:"s" == categoria_atual %}selected{% endif %}>{{ cat.nome }}</option>
        {% endfor %}
    </select>

    <button type="submit" class="bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-800">Filtrar</button>
    {% if termo_atual or status_atual or categoria_atual %}
        <a href="{% url 'tarefas:lista' %}" class="px-4 py-2 text-gray-600 hover:text-gray-800">Limpar</a>
    {% endif %}
</form>
```

| Detalhe | Função |
|---|---|
| `method="get"` | Filtros vão para a URL → permite favoritar, compartilhar, voltar pelo browser |
| `value="{{ termo_atual }}"` | Mantém o valor digitado após submeter |
| `selected` condicional | Lembra qual opção foi escolhida |
| `cat.id|stringformat:"s"` | Converte o int para string para comparar com o valor da querystring (que sempre é string) |
| Link "Limpar" | Atalho para resetar todos os filtros |

---

## 3. Testar

```bash
python manage.py runserver
```

Acesse `/tarefas/`:

- Digite no campo de busca → submeta → URL fica `?q=...`
- Escolha um status → URL fica `?status=PENDENTE`
- Combine os três
- Clique em "Limpar"

---

## 4. Onde mora a regra (revisão da Aula 08)

- "Como filtrar pendentes" → **View** (por enquanto). Quando esse `if status: qs = qs.filter(...)` se repetir em outras views, vira hora de mover para **Manager / QuerySet** customizado
- "Form de filtros usar `method=get`" → **Template** (decisão de UX)
- "Pesquisa case-insensitive" → **View** (`__icontains` é detalhe da query)

---

## 5. O que entregamos

- Sistema multiusuário rodando em MySQL
- Layout com Tailwind via CDN
- Auth com User customizado, signup/login/logout
- CRUD completo de tarefas escopado por usuário
- Categorias gerenciadas pelo admin
- Filtros e busca
- Mensagens flash, validação de form, estado vazio
- Cada regra de negócio numa camada que faz sentido

```
app/
├── config/                    # settings, urls, wsgi
├── core/                      # home + layout
├── accounts/                  # User customizado, signup, login, logout
├── categorias/                # model + admin
├── tarefas/                   # model, forms, views (CBVs), urls, templates
├── templates/base.html
├── static/
├── .env
├── requirements.txt
└── manage.py
```

---

## 6. Próximos passos

Quando tudo isso virar pequeno demais, esses são os caminhos naturais:

| Próximo passo | Quando faz sentido |
|---|---|
| **Testes** (`TestCase`, `Client`) | Antes de qualquer feature séria — agora |
| **Manager / QuerySet customizado** | Quando o mesmo `filter` aparecer em 3+ lugares |
| **Service layer** (`services.py`) | Quando uma operação tocar vários models, fizer I/O ou precisar de `transaction.atomic` |
| **Histórico de mudanças** | Auditoria (quem mudou o que, quando) — combina com service |
| **Upload de anexos na tarefa** (`FileField`) | Tópicos: `MEDIA_URL`, validação de tipo, segurança |
| **Geração de PDF** (`WeasyPrint`) | Relatório semanal exportável |
| **Integração com IA** (Claude / OpenAI) | Sugerir categoria automática a partir da descrição |
| **Deploy** (Railway, Render, Fly.io) | Quando tiver algo pra mostrar pro mundo |
| **API REST** com DRF | Quando precisar de mobile ou SPA |

---

## 7. Conclusão

O Django é generoso: dá CBV pronta, admin pronto, ORM pronto. O que diferencia código bom de código ruim **não é o framework** — é decidir conscientemente onde cada regra mora.

Você agora tem:
- Um sistema funcional
- Um modelo mental de camadas (Aula 08)
- Um terreno para evoluir

A próxima vez que aparecer uma feature nova, abra a Aula 08 de novo. Você vai saber onde colocar.

Boa jornada.

---

## Exercício final

1. Implemente os filtros e a busca
2. Teste cada combinação
3. Escolha **um** dos próximos passos da seção 6 e faça uma POC numa branch (sem precisar terminar — só pra explorar)
