from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=80, unique=True)
    cor = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text='Cor em formato hex, ex: #3B82F6',
    )
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.nome
