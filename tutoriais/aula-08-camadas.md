# Aula 08 — Camadas do Django (Revisão Prática)

## Objetivo

O sistema funciona. Hora de **olhar pra trás** e mapear: cada decisão que tomamos foi colocar uma regra numa camada. Saber **por que ali** (e não em outra) é o que diferencia código que envelhece bem de código que vira bola de neve.

Esta aula é **revisão consolidada** sobre o código que você já escreveu — sem novos features.

---

## 1. O mapa

```
URL  ─►  View  ─►  Form         (entrada / orquestração HTTP)
                └► Manager      (consultas reutilizáveis — em breve)
                └► Service      (regra rica, multi-model, transação — em breve)
                     └► Model   (forma do dado + regra de UM registro)
       Template                 (apresentação)
```

| Camada | Pergunta-chave |
|---|---|
| **URL** | Que caminho responde por isso? |
| **View** | Quem está logado? Que dados pegar? Que template renderizar? Para onde redirecionar? |
| **Form** | A entrada do usuário é válida? |
| **Model** | Qual a forma do dado? Que regra vale **sempre** sobre um registro? |
| **Manager / QuerySet** | Como buscar isso? *(introduzido na Aula 09)* |
| **Service** | Como orquestrar uma operação que toca vários models ou tem efeito colateral? *(tópico de evolução)* |
| **Template** | Como mostrar isso pro humano? |

---

## 2. Vamos olhar regra por regra

Pegue o seu próprio código aberto e responda: cada uma das regras abaixo, **onde mora?**

### 2.1 "Categoria não pode ter nome duplicado"

```python
# categorias/models.py
nome = models.CharField(max_length=80, unique=True)
```

→ **Model**. É invariante de UM registro: vale **sempre**, mesmo se o dado vier do admin, do shell, de um job. O banco vai criar um índice único e bloquear duplicatas no nível mais baixo possível.

### 2.2 "Listar categorias em ordem alfabética"

```python
# categorias/models.py
class Meta:
    ordering = ['nome']
```

→ **Model** (Meta). Aplicar na view com `.order_by('nome')` toda vez seria espalhar a regra. No `Meta`, vira padrão.

### 2.3 "Quando status virar Concluída, preencher concluida_em"

```python
# tarefas/models.py
def save(self, *args, **kwargs):
    if self.status == self.Status.CONCLUIDA and self.concluida_em is None:
        self.concluida_em = timezone.now()
    ...
```

→ **Model** (`save`). Regra que olha **só o próprio registro** e não tem efeito colateral em outras tabelas. Se um dia a regra crescer ("ao concluir, criar histórico, mandar e-mail"), aí migramos para **service**.

### 2.4 "Tarefa pertence a uma categoria, e ao apagar a categoria deve falhar se houver tarefas"

```python
# tarefas/models.py
categoria = models.ForeignKey(
    'categorias.Categoria',
    on_delete=models.PROTECT,
    related_name='tarefas',
)
```

→ **Model**. A regra de integridade referencial mora no schema do banco. Tentar resolver isso em código (ex: na view, antes de deletar) seria mais frágil — o banco continuaria deixando passar.

### 2.5 "Título precisa ter pelo menos 3 caracteres"

```python
# tarefas/forms.py
def clean_titulo(self):
    titulo = self.cleaned_data['titulo'].strip()
    if len(titulo) < 3:
        raise forms.ValidationError('Título deve ter pelo menos 3 caracteres.')
    return titulo
```

→ **Form**. É validação de **entrada externa**: protege contra o que vem do navegador. Não está no model porque é uma regra de UI/UX (poderíamos importar tarefas de uma planilha histórica com títulos curtos sem que isso devesse falhar).

> Se a regra fosse "**nunca, em nenhuma hipótese**, aceitar título com menos de 3 caracteres", o lugar seria o `clean()` do model. Distinguir isso é parte da disciplina.

### 2.6 "Usuário só vê e edita as próprias tarefas"

```python
# tarefas/views.py
def get_queryset(self):
    return Tarefa.objects.filter(usuario=self.request.user)
```

→ **View**. Por que? Porque depende do **request** (quem está logado **agora**). Regra de domínio que depende do contexto da requisição mora na view. O model não tem ideia de "quem está logado".

### 2.7 "Ao criar uma tarefa, o usuário é o que está logado"

```python
# tarefas/views.py
def form_valid(self, form):
    form.instance.usuario = self.request.user
    return super().form_valid(form)
```

→ **View** (mesma razão). Note que **não** colocamos `usuario` no `Meta.fields` do form — assim o usuário não consegue forjar o dono da tarefa via input HTML.

### 2.8 "Acesso à página /tarefas/ exige login"

```python
class TarefaListView(LoginRequiredMixin, ListView):
    ...
```

→ **View** (mixin). Regra de autorização HTTP — vive na borda HTTP.

### 2.9 "Mostrar a tarefa concluída com badge verde"

```html
<span class="px-2 py-1 rounded text-xs
    {% if tarefa.status == 'CONCLUIDA' %}bg-green-100 text-green-800{% endif %}">
    {{ tarefa.get_status_display }}
</span>
```

→ **Template**. É decisão de **apresentação**, não de domínio.

### 2.10 "Após criar uma tarefa, mostrar mensagem de sucesso"

```python
class TarefaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    success_message = 'Tarefa "%(titulo)s" criada com sucesso!'
```

→ **View**. Mensagem flash é parte da resposta HTTP.

---

## 3. Cartão de bolso — heurística de decisão

Diante de uma regra nova, pergunte **nessa ordem**:

1. É regra de **um único registro**, sempre verdadeira? → **Model**
2. É **integridade referencial** (relacionamento, unicidade, default)? → **Model** / **Meta**
3. É **validação de entrada do usuário** via formulário? → **Form** (`clean_<campo>` ou `clean()`)
4. É **decisão sobre quem pode acessar / o que mostrar** baseada no request? → **View**
5. É **consulta reutilizável** (a mesma query aparecendo em vários lugares)? → **Manager / QuerySet** *(Aula 09)*
6. É **operação que toca vários models, faz I/O ou precisa de transação atômica**? → **Service**
7. É só **como aparece** na tela? → **Template**

---

## 4. Anti-padrões comuns (e o que está errado)

| Anti-padrão | Por que é ruim |
|---|---|
| `if request.user.is_staff:` no template | Lógica de domínio no template — quebra reuso e dificulta teste |
| `Tarefa.objects.filter(...).exclude(...).filter(...)` repetido em 5 views | DRY violado — quando a regra mudar, vai esquecer algum lugar |
| `if status == 'PENDENTE': ... elif status == 'EM_ANDAMENTO': ...` espalhado | Strings mágicas. Use `Tarefa.Status.PENDENTE` (vem do `TextChoices`) |
| Sobrescrever `save()` para enviar e-mail | Efeito colateral oculto. Vai ser executado em testes, em fixtures, em scripts. Use service |
| `clean()` do form fazendo SQL pesado | Form é entrada — deve ser barato. Validação cara: model.clean() ou service |

---

## 5. Pequeno refactor (opcional)

No template `tarefas/lista.html` temos:

```html
{% if tarefa.status == 'PENDENTE' %}bg-yellow-100 text-yellow-800{% endif %}
{% if tarefa.status == 'EM_ANDAMENTO' %}bg-blue-100 text-blue-800{% endif %}
{% if tarefa.status == 'CONCLUIDA' %}bg-green-100 text-green-800{% endif %}
```

São strings mágicas no template. Em projeto real, valeria criar uma **template tag** que devolve a classe a partir do status, deixando o mapeamento num só lugar Python. Por enquanto, tudo bem — o código é curto e está num só lugar.

---

## Exercício

Pegue 3 features hipotéticas abaixo e diga **em qual camada cada regra mora**. Justifique:

1. "Tarefa não pode ter prazo no passado"
2. "Listar as 5 tarefas mais recentes do usuário no dashboard"
3. "Ao concluir uma tarefa, registrar entrada num log e enviar e-mail de notificação"
4. "Mostrar 'Atrasada' em vermelho se o prazo passou"
5. "Apenas admins podem ver a lista de todos os usuários"

(Respostas no fim do arquivo se quiser conferir, mas tente primeiro.)

---

## Próxima aula

[Aula 09 — Filtros, busca + encerramento](aula-09-filtros-e-encerramento.md).

---

<details>
<summary>Respostas do exercício</summary>

1. **Form** (`clean_prazo`) — validação de entrada. Se for invariante absoluto, **Model.clean()**.
2. **Manager / QuerySet** (`Tarefa.objects.do_usuario(u).recentes(5)`) consumido por uma **View** que renderiza no template.
3. **Service** — efeito colateral (e-mail) e múltiplas escritas (Tarefa + Log) num só lugar atômico.
4. **Template** (formatação) — calculado num **method do model** (`@property def is_atrasada`) ou **template tag**, mas a decoração visual fica no template.
5. **View** (`PermissionRequiredMixin` ou checagem em `dispatch`) — autorização HTTP.

</details>
