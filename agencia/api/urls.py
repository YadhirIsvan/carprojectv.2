from django.urls import path, include
from .views import (
    # Catálogos públicos
    MarcaListView,
    ModeloListView,
    ModelosPorMarcaView,
    ServicioTallerListView,
    
    # Views específicas por rol (importadas de submódulos)
    cliente_views,
    asistente_views,
    taller_views,
)

app_name = 'agencia'

urlpatterns = [
    # ==========================================
    # CATÁLOGOS PÚBLICOS
    # ==========================================
    path('marcas/', MarcaListView.as_view(), name='marcas-list'),
    path('marcas/<int:pk>/modelos/', ModelosPorMarcaView.as_view(), name='modelos-por-marca'),
    path('servicios-taller/', ServicioTallerListView.as_view(), name='servicios-taller'),
    
    # ==========================================
    # RUTAS POR ROL
    # ==========================================
    path('cliente/', include('agencia.api.urls_cliente')),
    path('asistente/', include('agencia.api.urls_asistente')),
    path('taller/', include('agencia.api.urls_taller')),
]