# Aula 07 — CRUD de Tarefa para o Usuário

## Objetivo

Permitir que o usuário logado **liste, crie, edite e exclua** suas próprias tarefas pela interface (sem admin). Introduz CBVs, `ModelForm`, escopo por usuário e mensagens flash.

---

## 1. ModelForm

`tarefas/forms.py`:

```python
from django import forms

from .models import Tarefa


CLASSE_INPUT = (
    'w-full border border-gray-300 rounded px-3 py-2 '
    'focus:outline-none focus:border-blue-500'
)


class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['titulo', 'descricao', 'status', 'prioridade', 'categoria']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': CLASSE_INPUT}),
            'descricao': forms.Textarea(attrs={'class': CLASSE_INPUT, 'rows': 4}),
            'status': forms.Select(attrs={'class': CLASSE_INPUT}),
            'prioridade': forms.Select(attrs={'class': CLASSE_INPUT}),
            'categoria': forms.Select(attrs={'class': CLASSE_INPUT}),
        }

    def clean_titulo(self):
        titulo = self.cleaned_data['titulo'].strip()
        if len(titulo) < 3:
            raise forms.ValidationError('Título deve ter pelo menos 3 caracteres.')
        return titulo
```

### Pontos a entender

| Item | Função |
|---|---|
| `ModelForm` | Form gerado automaticamente a partir de um model |
| `Meta.fields` | Quais campos do model entram no form. **Nunca use `'__all__'`** — sempre liste explicitamente para não expor campos sensíveis sem perceber |
| `widgets` | Customiza HTML/atributos dos inputs (aqui usamos para aplicar classes do Tailwind) |
| `clean_<campo>` | Validação específica de um campo. Recebe o valor já tipado, retorna o valor (possivelmente modificado) ou levanta `ValidationError` |

> Note que **não incluímos `usuario` nos `fields`** — quem deve preencher é a view, automaticamente, com `request.user`. Se deixássemos no form, o usuário poderia escolher para quem ele cria a tarefa.

---

## 2. Views (CBVs)

`tarefas/views.py`:

```python
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import TarefaForm
from .models import Tarefa


class TarefaListView(LoginRequiredMixin, ListView):
    model = Tarefa
    template_name = 'tarefas/lista.html'
    context_object_name = 'tarefas'
    paginate_by = 20

    def get_queryset(self):
        return Tarefa.objects.filter(usuario=self.request.user).select_related('categoria')


class TarefaDetailView(LoginRequiredMixin, DetailView):
    model = Tarefa
    template_name = 'tarefas/detalhe.html'
    context_object_name = 'tarefa'

    def get_queryset(self):
        return Tarefa.objects.filter(usuario=self.request.user)


class TarefaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Tarefa
    form_class = TarefaForm
    template_name = 'tarefas/form.html'
    success_url = reverse_lazy('tarefas:lista')
    success_message = 'Tarefa "%(titulo)s" criada com sucesso!'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class TarefaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Tarefa
    form_class = TarefaForm
    template_name = 'tarefas/form.html'
    success_url = reverse_lazy('tarefas:lista')
    success_message = 'Tarefa "%(titulo)s" atualizada!'

    def get_queryset(self):
        return Tarefa.objects.filter(usuario=self.request.user)


class TarefaDeleteView(LoginRequiredMixin, DeleteView):
    model = Tarefa
    template_name = 'tarefas/confirmar_exclusao.html'
    success_url = reverse_lazy('tarefas:lista')

    def get_queryset(self):
        return Tarefa.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f'Tarefa "{self.object.titulo}" excluída.')
        return super().form_valid(form)
```

### Pontos cruciais

#### `LoginRequiredMixin`

Usuário não autenticado é redirecionado para `LOGIN_URL`. Aplicado em todas as views.

#### `get_queryset()` filtrado

```python
def get_queryset(self):
    return Tarefa.objects.filter(usuario=self.request.user)
```

Isso garante o **escopo por usuário**: a `ListView` só mostra suas tarefas; a `DetailView`, `UpdateView` e `DeleteView` retornam **404** se o `pk` da URL pertence a outro usuário (porque o `get_object_or_404` opera dentro do queryset filtrado).

> **Por que 404 e não 403?** Não vazamos a informação de que aquela tarefa existe.

#### `form_valid()` no Create

```python
def form_valid(self, form):
    form.instance.usuario = self.request.user
    return super().form_valid(form)
```

Como `usuario` não está no form (decisão da seção anterior), preenchemos manualmente antes de salvar.

#### `SuccessMessageMixin`

Adiciona automaticamente uma mensagem flash quando o form é válido. O placeholder `%(titulo)s` puxa o valor do model salvo.

#### `select_related('categoria')`

Otimização: evita uma query adicional para cada categoria ao listar. Para 50 tarefas, vira 1 query em vez de 51.

---

## 3. URLs

`tarefas/urls.py`:

```python
from django.urls import path

from . import views

app_name = 'tarefas'

urlpatterns = [
    path('', views.TarefaListView.as_view(), name='lista'),
    path('nova/', views.TarefaCreateView.as_view(), name='criar'),
    path('<int:pk>/', views.TarefaDetailView.as_view(), name='detalhe'),
    path('<int:pk>/editar/', views.TarefaUpdateView.as_view(), name='editar'),
    path('<int:pk>/excluir/', views.TarefaDeleteView.as_view(), name='excluir'),
]
```

`config/urls.py`:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('accounts.urls')),
    path('tarefas/', include('tarefas.urls')),
    path('', include('core.urls')),
]
```

---

## 4. Templates

```bash
mkdir -p tarefas/templates/tarefas
```

### 4.1 `tarefas/templates/tarefas/lista.html`

```html
{% extends 'base.html' %}
{% block title %}Minhas Tarefas{% endblock %}

{% block content %}
<div class="flex items-center justify-between mb-6">
    <h1 class="text-2xl font-bold">Minhas Tarefas</h1>
    <a href="{% url 'tarefas:criar' %}" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        + Nova tarefa
    </a>
</div>

{% if tarefas %}
    <div class="bg-white shadow-sm rounded-lg overflow-hidden">
        <table class="w-full">
            <thead class="bg-gray-100 text-left text-sm text-gray-700">
                <tr>
                    <th class="px-4 py-3">Título</th>
                    <th class="px-4 py-3">Categoria</th>
                    <th class="px-4 py-3">Status</th>
                    <th class="px-4 py-3">Prioridade</th>
                    <th class="px-4 py-3 text-right">Ações</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
                {% for tarefa in tarefas %}
                <tr>
                    <td class="px-4 py-3">
                        <a href="{% url 'tarefas:detalhe' tarefa.pk %}" class="text-blue-600 hover:underline font-medium">
                            {{ tarefa.titulo }}
                        </a>
                    </td>
                    <td class="px-4 py-3">
                        <span class="inline-flex items-center gap-2">
                            <span class="w-3 h-3 rounded-full" style="background: {{ tarefa.categoria.cor }}"></span>
                            {{ tarefa.categoria.nome }}
                        </span>
                    </td>
                    <td class="px-4 py-3">
                        <span class="px-2 py-1 rounded text-xs
                            {% if tarefa.status == 'PENDENTE' %}bg-yellow-100 text-yellow-800{% endif %}
                            {% if tarefa.status == 'EM_ANDAMENTO' %}bg-blue-100 text-blue-800{% endif %}
                            {% if tarefa.status == 'CONCLUIDA' %}bg-green-100 text-green-800{% endif %}">
                            {{ tarefa.get_status_display }}
                        </span>
                    </td>
                    <td class="px-4 py-3 text-sm">{{ tarefa.get_prioridade_display }}</td>
                    <td class="px-4 py-3 text-right text-sm space-x-3">
                        <a href="{% url 'tarefas:editar' tarefa.pk %}" class="text-blue-600 hover:underline">Editar</a>
                        <a href="{% url 'tarefas:excluir' tarefa.pk %}" class="text-red-600 hover:underline">Excluir</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
{% else %}
    <div class="bg-white p-12 rounded-lg shadow-sm text-center">
        <p class="text-gray-500 mb-4">Nenhuma tarefa por aqui ainda.</p>
        <a href="{% url 'tarefas:criar' %}" class="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
            Criar primeira tarefa
        </a>
    </div>
{% endif %}
{% endblock %}
```

### 4.2 `tarefas/templates/tarefas/form.html`

```html
{% extends 'base.html' %}
{% block title %}{% if object %}Editar tarefa{% else %}Nova tarefa{% endif %}{% endblock %}

{% block content %}
<div class="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow">
    <h1 class="text-2xl font-bold mb-6">
        {% if object %}Editar tarefa{% else %}Nova tarefa{% endif %}
    </h1>

    <form method="post" class="space-y-4">
        {% csrf_token %}

        {% if form.non_field_errors %}
            <div class="bg-red-50 text-red-800 p-3 rounded">{{ form.non_field_errors }}</div>
        {% endif %}

        {% for field in form %}
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ field.label }}</label>
                {{ field }}
                {% if field.help_text %}
                    <p class="text-xs text-gray-500 mt-1">{{ field.help_text }}</p>
                {% endif %}
                {% if field.errors %}
                    <div class="text-sm text-red-600 mt-1">{{ field.errors }}</div>
                {% endif %}
            </div>
        {% endfor %}

        <div class="flex gap-2 pt-4">
            <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
                {% if object %}Salvar{% else %}Criar{% endif %}
            </button>
            <a href="{% url 'tarefas:lista' %}" class="px-6 py-2 border border-gray-300 rounded hover:bg-gray-50">
                Cancelar
            </a>
        </div>
    </form>
</div>
{% endblock %}
```

### 4.3 `tarefas/templates/tarefas/detalhe.html`

```html
{% extends 'base.html' %}
{% block title %}{{ tarefa.titulo }}{% endblock %}

{% block content %}
<div class="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow">
    <div class="flex items-start justify-between mb-4">
        <h1 class="text-2xl font-bold">{{ tarefa.titulo }}</h1>
        <span class="px-3 py-1 rounded text-sm
            {% if tarefa.status == 'PENDENTE' %}bg-yellow-100 text-yellow-800{% endif %}
            {% if tarefa.status == 'EM_ANDAMENTO' %}bg-blue-100 text-blue-800{% endif %}
            {% if tarefa.status == 'CONCLUIDA' %}bg-green-100 text-green-800{% endif %}">
            {{ tarefa.get_status_display }}
        </span>
    </div>

    <div class="space-y-2 text-sm text-gray-600 mb-6">
        <p><strong>Categoria:</strong>
            <span class="inline-flex items-center gap-2">
                <span class="w-3 h-3 rounded-full" style="background: {{ tarefa.categoria.cor }}"></span>
                {{ tarefa.categoria.nome }}
            </span>
        </p>
        <p><strong>Prioridade:</strong> {{ tarefa.get_prioridade_display }}</p>
        <p><strong>Criada em:</strong> {{ tarefa.criada_em|date:"d/m/Y H:i" }}</p>
        {% if tarefa.concluida_em %}
            <p><strong>Concluída em:</strong> {{ tarefa.concluida_em|date:"d/m/Y H:i" }}</p>
        {% endif %}
    </div>

    {% if tarefa.descricao %}
        <div class="bg-gray-50 p-4 rounded mb-6">
            <p class="whitespace-pre-line">{{ tarefa.descricao }}</p>
        </div>
    {% endif %}

    <div class="flex gap-2">
        <a href="{% url 'tarefas:editar' tarefa.pk %}" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Editar</a>
        <a href="{% url 'tarefas:excluir' tarefa.pk %}" class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Excluir</a>
        <a href="{% url 'tarefas:lista' %}" class="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50">Voltar</a>
    </div>
</div>
{% endblock %}
```

### 4.4 `tarefas/templates/tarefas/confirmar_exclusao.html`

```html
{% extends 'base.html' %}
{% block title %}Excluir tarefa{% endblock %}

{% block content %}
<div class="max-w-md mx-auto bg-white p-8 rounded-lg shadow">
    <div class="bg-red-50 border border-red-200 p-4 rounded mb-4">
        <h2 class="text-xl font-bold text-red-800 mb-2">Excluir tarefa?</h2>
        <p class="text-gray-700">
            Você está prestes a excluir <strong>"{{ object.titulo }}"</strong>.
            Esta ação não pode ser desfeita.
        </p>
    </div>

    <form method="post" class="flex gap-2">
        {% csrf_token %}
        <button type="submit" class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Excluir</button>
        <a href="{% url 'tarefas:lista' %}" class="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50">Cancelar</a>
    </form>
</div>
{% endblock %}
```

---

## 5. Atualizar a navbar do `base.html`

Adicione um link para "Tarefas" quando logado:

```html
{% if user.is_authenticated %}
    <a href="{% url 'tarefas:lista' %}" class="text-gray-700 hover:text-blue-600">Tarefas</a>
    <span class="text-gray-500">Olá, {{ user.username }}</span>
    <form method="post" action="{% url 'accounts:logout' %}" class="inline">
        {% csrf_token %}
        <button type="submit" class="text-gray-700 hover:text-red-600">Sair</button>
    </form>
{% else %}
    ...
{% endif %}
```

---

## 6. Testar o fluxo completo

1. Cadastre um usuário (`/contas/cadastrar/`)
2. Faça login
3. Clique em "Tarefas" → lista vazia, com CTA "Criar primeira tarefa"
4. Crie uma tarefa
5. Note a mensagem flash verde no topo
6. Edite, mude o status para "Concluída" — note o badge verde e a data automática no detalhe
7. Excluir → tela de confirmação → exclui
8. Crie um **segundo usuário** em outro navegador. Verifique que ele não vê as tarefas do primeiro

---

## Exercício

1. Crie `forms.py` com `TarefaForm` (com Tailwind nos widgets e `clean_titulo`)
2. Implemente as 5 CBVs com `LoginRequiredMixin` e `get_queryset` filtrado
3. Crie `tarefas/urls.py` e inclua no `config/urls.py`
4. Os 4 templates (lista, form, detalhe, confirmar exclusão)
5. Atualize a navbar
6. Teste o fluxo completo com 2 usuários diferentes — confirme o isolamento

---

## Próxima aula

[Aula 08 — Camadas do Django (revisão prática)](aula-08-camadas.md).
