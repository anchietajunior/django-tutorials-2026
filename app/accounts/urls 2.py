from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path(
        'entrar/',
        LoginView.as_view(template_name='accounts/login.html'),
        name='login',
    ),
    path('sair/', LogoutView.as_view(), name='logout'),
    path('cadastrar/', views.SignupView.as_view(), name='signup'),
]
