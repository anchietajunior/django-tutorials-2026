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
