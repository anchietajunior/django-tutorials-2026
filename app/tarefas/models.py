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
