# Aula 07 — Upload de imagem no post

## Objetivo

Permitir que cada post tenha uma **imagem opcional** anexada. O arquivo é enviado pelo formulário, salvo no servidor (em `media/`) e exibido na tela de detalhe.

```
[ form com input file ]──► [ ImageField ]──► media/posts/<arquivo>
                                         │
                                         └──► <img src="{{ post.imagem.url }}">
```

> **Onde mora a regra?** Pela hierarquia da [Aula 06](aula-06-regras-de-negocio.md), validação de **input do usuário** vive no **form** — não no model. O model só vê o arquivo se ele já passou na validação do form.

---

## 1. Instalar Pillow

`ImageField` depende da biblioteca **Pillow** para abrir e validar imagens.

```bash
pip install Pillow
```

> Se aparecer erro de compilação no Linux, instale antes: `sudo apt install python3-dev libjpeg-dev zlib1g-dev`.

---

## 2. Configurar `MEDIA_URL` e `MEDIA_ROOT`

O Django separa **arquivos estáticos** (CSS, JS — versionados no Git) de **arquivos de mídia** (uploads do usuário — fora do Git).

Em `config/settings.py`, no fim do arquivo:

```python
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

| Setting | Função |
|---|---|
| `MEDIA_URL` | Prefixo de URL onde os uploads são servidos (ex.: `/media/posts/foto.jpg`) |
| `MEDIA_ROOT` | Pasta no disco onde os arquivos são salvos |

Adicione `media/` ao `.gitignore` (uploads não vão pro repositório):

```
media/
```

---

## 3. Servir uploads em desenvolvimento

Em produção, um servidor web (nginx) entrega `media/`. Em dev, o próprio Django pode servir — basta pedir.

`config/urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('accounts.urls')),
    path('posts/', include('posts.urls')),
    path('', views.home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

> O `if settings.DEBUG:` é importante. Em produção (`DEBUG=False`) essa rota é silenciosamente desligada — o servidor web é quem cuida.

---

## 4. Adicionar `ImageField` ao Post

Em `posts/models.py`:

```python
class Post(models.Model):
    class Status(models.TextChoices):
        EM_PROGRESSO = 'em_progresso', 'Em progresso'
        FINALIZADO = 'finalizado', 'Finalizado'

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    titulo = models.CharField(max_length=120)
    descricao = models.TextField()
    imagem = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.EM_PROGRESSO,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo
```

| Detalhe | Função |
|---|---|
| `upload_to='posts/'` | Subpasta dentro de `MEDIA_ROOT` onde os arquivos são salvos. Resultado: `media/posts/foto.jpg` |
| `blank=True` | No formulário, o campo é opcional |
| `null=True` | No banco, aceita `NULL` — post sem imagem |

Migrar:

```bash
python manage.py makemigrations posts
python manage.py migrate
```

---

## 5. Incluir o campo no form

`posts/forms.py`:

```python
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'descricao', 'imagem', 'status']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'descricao': forms.Textarea(attrs={'class': 'w-full border rounded px-3 py-2', 'rows': 5}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'w-full text-sm'}),
            'status': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2'}),
        }
```

`ClearableFileInput` é o widget padrão para arquivos — adiciona um checkbox "Limpar" quando já há arquivo enviado (útil no edit).

---

## 6. **O detalhe que TODO MUNDO esquece**: `enctype="multipart/form-data"`

Formulários HTML, por padrão, mandam dados como texto. Para enviar arquivos é preciso outro encoding. Em `posts/templates/posts/form.html`:

```html
<form method="post" enctype="multipart/form-data" class="space-y-4">
```

> **Esqueceu?** O upload silenciosamente **não acontece**: o form salva sem erro, mas o `ImageField` continua vazio. É a pegadinha #1 de iniciantes em Django.

E nas views, o `CreateView`/`UpdateView` já leem `request.FILES` automaticamente — não precisa mexer em nada lá.

---

## 7. Mostrar a imagem no detalhe

Em `posts/templates/posts/detail.html`, antes do `descricao`:

```html
<article class="bg-white p-6 rounded shadow max-w-3xl mx-auto">
    <h1 class="text-3xl font-bold mb-2">{{ post.titulo }}</h1>
    <p class="text-sm text-gray-500 mb-4">
        {{ post.get_status_display }} · {{ post.criado_em|date:"d/m/Y H:i" }}
    </p>

    {% if post.imagem %}
        <img src="{{ post.imagem.url }}" alt="{{ post.titulo }}"
             class="w-full max-h-96 object-cover rounded mb-4">
    {% endif %}

    <div class="prose mb-6 whitespace-pre-line">{{ post.descricao }}</div>

    <div class="flex gap-3">
        <a href="{% url 'posts:update' post.pk %}" class="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600">Editar</a>
        <a href="{% url 'posts:delete' post.pk %}" class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Excluir</a>
        <a href="{% url 'posts:list' %}" class="text-gray-600 hover:underline self-center ml-auto">Voltar</a>
    </div>
</article>
```

| Pedaço | Função |
|---|---|
| `{% if post.imagem %}` | Não tenta renderizar `<img>` se o post não tem imagem |
| `post.imagem.url` | Atributo do `ImageField`. Devolve a URL completa, montada com `MEDIA_URL` + caminho do arquivo |

(Opcional) miniatura na lista (`list.html`):

```html
{% if post.imagem %}
    <img src="{{ post.imagem.url }}" alt="" class="w-12 h-12 object-cover rounded mr-3 inline-block">
{% endif %}
```

---

## 8. Testar

```bash
python manage.py runserver
```

1. Logado, vá em **Novo post**, preencha tudo e selecione uma imagem (jpg/png).
2. Salvar → o detail deve mostrar a imagem.
3. Confira no disco: existe um arquivo em `app/media/posts/<nome>.jpg`.
4. Edite o post e use o checkbox **Limpar** → a imagem some.
5. Crie um post **sem** imagem → detail funciona normal, sem `<img>`.

---

## 9. Validação de tamanho — no form (relembrando a Aula 06)

Pillow valida que o arquivo é **mesmo** uma imagem (rejeita `.exe` renomeado para `.jpg`). Falta limitar o tamanho.

A pergunta da [Aula 06](aula-06-regras-de-negocio.md): **onde mora essa regra?** Resposta: **no form**. Validar input do usuário é trabalho do form — se o tamanho passar, o model nunca vê o arquivo. Se mudássemos para o model (em `clean()` ou no `save()`), o erro só apareceria depois que o framework já tivesse aceitado o request, e a mensagem voltaria menos amigável.

`posts/forms.py`:

```python
class PostForm(forms.ModelForm):
    # ... Meta ...

    MAX_TAMANHO_MB = 5

    def clean_imagem(self):
        imagem = self.cleaned_data.get('imagem')
        if imagem and imagem.size > self.MAX_TAMANHO_MB * 1024 * 1024:
            raise forms.ValidationError(
                f'Imagem muito grande (máx {self.MAX_TAMANHO_MB} MB).'
            )
        return imagem
```

| Detalhe | Função |
|---|---|
| `clean_<campo>` | Hook do Django para validar um campo individualmente após `cleaned_data` ser populado |
| `imagem.size` | Tamanho em bytes (atributo do objeto `UploadedFile`) |

Teste enviando um arquivo > 5MB — deve aparecer a mensagem de erro abaixo do campo.

---

## Cuidados de segurança

| Risco | Mitigação aqui |
|---|---|
| Arquivo malicioso disfarçado | Pillow tenta abrir como imagem — falha em arquivos não-imagem |
| Upload gigante esgotando disco | Validação `clean_imagem` |
| Acesso a uploads de outros usuários | Em produção, considere salvar imagens em diretórios por usuário (`upload_to='posts/<user_id>/'`) |
| Nome de arquivo conflitante | Django acrescenta sufixo aleatório se o nome já existir |

---

## Exercício

1. Instale Pillow.
2. Configure `MEDIA_URL`, `MEDIA_ROOT` e o `static()` no `config/urls.py`.
3. Adicione `imagem = ImageField(...)` ao Post e rode a migration.
4. Inclua `imagem` em `PostForm.Meta.fields`.
5. **Não esqueça** o `enctype="multipart/form-data"` no `<form>`.
6. Renderize a imagem no detail com `{% if post.imagem %}`.
7. Crie um post com imagem, um sem imagem — ambos funcionam.
8. (Opcional) Implemente a validação de tamanho.

---

## 🔁 Vindo do Rails

| Conceito | Rails | Django |
|---|---|---|
| Anexar arquivo a um model | `has_one_attached :imagem` (Active Storage) | `imagem = models.ImageField(upload_to='posts/')` |
| Dependência de imagem | gem `image_processing` (libvips/MiniMagick) | biblioteca **Pillow** (`pip install Pillow`) |
| Validação automática "é imagem mesmo?" | Validators (`validates :imagem, content_type: ['image/jpg']`) | Pillow tenta abrir o arquivo no `clean()` do `ImageField` |
| Configurar storage | `config/storage.yml` (`local`, `amazon`, `gcs`...) | `MEDIA_URL`/`MEDIA_ROOT` (local); `django-storages` para S3/GCS |
| URL do arquivo | `url_for(post.imagem)` ou `rails_blob_url(post.imagem)` | `post.imagem.url` |
| Caminho local no disco | `ActiveStorage::Blob.service.send(:path_for, blob.key)` (ginástica) | `post.imagem.path` (direto, atributo do `FieldFile`) |
| Servir uploads em dev | Rota `/rails/active_storage/...` automática | `static(MEDIA_URL, document_root=MEDIA_ROOT)` no `urls.py` (manual) |
| Servir uploads em prod | nginx/CDN apontando para `Rails.application.routes` | nginx servindo `MEDIA_ROOT/` (Django **não** serve estático em produção) |
| Multipart form | `form_with model: @post, multipart: true` (ou auto se tem `file_field`) | `<form enctype="multipart/form-data">` (manual sempre) |
| Limpar arquivo no edit | Checkbox automático em `form.file_field` | `forms.ClearableFileInput` (default do `ImageField`) |
| Validar tamanho | `validates :imagem, size: { less_than: 5.megabytes }` (gem `active_storage_validations`) | `def clean_imagem(self): ... raise forms.ValidationError(...)` |

> 💎 **`enctype="multipart/form-data"` é manual.** No Rails, `form_with model: @post` que contenha `file_field :imagem` automaticamente vira `multipart`. No Django, **você precisa colocar à mão** no `<form>`. Esquecer é a pegadinha #1 — o form salva sem erro e o `imagem` fica vazio. Em Rails, o framework te protege; em Django, ele confia em você.

> 💎 **Active Storage tem mais peças que `ImageField`.** Active Storage cria duas tabelas (`active_storage_blobs` e `active_storage_attachments`) e desacopla o arquivo do model. Permite anexar o mesmo blob a vários models, redimensionar com variantes, e trocar de storage backend sem migration. `ImageField` do Django é mais "antigo": uma coluna `varchar` que guarda o caminho relativo, ponto. Para anexar **um** arquivo simples a um model, é o suficiente. Para casos complexos, a comunidade usa `django-storages` + design próprio ou a app `django-cleanup`.

> 💎 **`MEDIA` é o oposto de `STATIC`.** A confusão é certa: `STATIC` é arquivo do **dev** (CSS, JS, ícones — versionado no Git). `MEDIA` é arquivo do **usuário** (uploads — fora do Git). No Rails, ambos passam pelo Active Storage ou pela pipeline — não há essa divisão tão explícita. Pense: `STATIC` = `app/assets/`, `MEDIA` = `storage/` do Active Storage local.

> 💎 **`post.imagem.url` vs `post.imagem.path`.** `url` é o que você bota no `<img src>` do navegador (`/media/posts/foo.jpg`). `path` é o caminho absoluto no disco (`/Users/.../app/media/posts/foo.jpg`). A próxima aula (PDF) usa `path` porque o WeasyPrint lê do disco, não via HTTP.

---

## Próxima aula

[Aula 08 — Geração de PDF do post](aula-08-pdf.md).
