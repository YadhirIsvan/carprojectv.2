from django.urls import path
from .views.taller_views import (
    # Servicios asignados
    MisServiciosListView,
    MiServicioDetailView,
    CambiarEstadoServicioView,
    
    # Progreso
    CrearProgresoServicioView,
    ListarProgresoServicioView,
    ActualizarProgresoServicioView,
    
    # Consultas
    ReservacionTallerDetailView,
    ServicioDetalleView,
)

app_name = 'taller'

urlpatterns = [
    # ==========================================
    # SERVICIOS ASIGNADOS
    # ==========================================
    path('mis-servicios/', MisServiciosListView.as_view(), name='mis-servicios-list'),
    path('mis-servicios/<int:pk>/', MiServicioDetailView.as_view(), name='mi-servicio-detail'),
    path('mis-servicios/<int:pk>/estado/', CambiarEstadoServicioView.as_view(), name='cambiar-estado-servicio'),
    
    # ==========================================
    # PROGRESO DE SERVICIOS
    # ==========================================
    path('servicios/<int:servicio_id>/progreso/', CrearProgresoServicioView.as_view(), name='crear-progreso'),
    path('servicios/<int:servicio_id>/progreso/listar/', ListarProgresoServicioView.as_view(), name='listar-progreso'),
    path('servicios/<int:servicio_id>/progreso/<int:pk>/', ActualizarProgresoServicioView.as_view(), name='actualizar-progreso'),
    
    # ==========================================
    # CONSULTAS
    # ==========================================
    path('reservaciones/<int:pk>/', ReservacionTallerDetailView.as_view(), name='reservacion-detail'),
    path('servicios/<int:pk>/detalle/', ServicioDetalleView.as_view(), name='servicio-detalle'),
]