from django.contrib import admin

from .models import Tarefa


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'status', 'prioridade', 'categoria', 'criada_em']
    list_filter = ['status', 'prioridade', 'categoria']
    search_fields = ['titulo', 'descricao']
