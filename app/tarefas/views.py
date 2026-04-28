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
