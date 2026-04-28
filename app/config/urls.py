from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('accounts.urls')),
    path('tarefas/', include('tarefas.urls')),
    path('', views.home, name='home'),
]
