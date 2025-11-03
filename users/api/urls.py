from django.urls import path
from .views import (
    # Autenticación
    LoginView,
    LogoutView,
    RefreshTokenView,
    MeView,
    
    # Perfil de usuario
    PerfilUsuarioView,
    CambiarPasswordView,
    
    # Catálogos
    TipoUsuarioListView,
    UsuarioListView,
    UsuarioDetailView,
)

app_name = 'users'

urlpatterns = [
    # ==========================================
    # AUTENTICACIÓN
    # ==========================================
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('auth/me/', MeView.as_view(), name='me'),
    
    # ==========================================
    # PERFIL DE USUARIO
    # ==========================================
    path('usuarios/perfil/', PerfilUsuarioView.as_view(), name='perfil'),
    path('usuarios/perfil/password/', CambiarPasswordView.as_view(), name='cambiar-password'),
    
    # ==========================================
    # CATÁLOGOS (ADMIN/ASISTENTE)
    # ==========================================
    path('tipos-usuarios/', TipoUsuarioListView.as_view(), name='tipos-usuarios'),
    path('usuarios/', UsuarioListView.as_view(), name='usuarios-list'),
    path('usuarios/<int:pk>/', UsuarioDetailView.as_view(), name='usuario-detail'),
]