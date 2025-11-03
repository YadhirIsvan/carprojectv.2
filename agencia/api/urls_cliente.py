from django.urls import path
from .views.cliente_views import (
    # Vehículos
    VehiculoClienteListCreateView,
    VehiculoClienteDetailView,
    
    # Solicitudes
    SolicitudClienteListCreateView,
    SolicitudClienteDetailView,
    
    # Reservaciones
    ReservacionClienteListView,
    ReservacionClienteDetailView,
    CancelarReservacionView,
    
    # Seguimiento
    ServiciosReservacionView,
    ProgresoServicioView,
)

app_name = 'cliente'

urlpatterns = [
    # ==========================================
    # VEHÍCULOS
    # ==========================================
    path('vehiculos/', VehiculoClienteListCreateView.as_view(), name='vehiculos-list-create'),
    path('vehiculos/<int:pk>/', VehiculoClienteDetailView.as_view(), name='vehiculo-detail'),
    
    # ==========================================
    # SOLICITUDES
    # ==========================================
    path('solicitudes/', SolicitudClienteListCreateView.as_view(), name='solicitudes-list-create'),
    path('solicitudes/<int:pk>/', SolicitudClienteDetailView.as_view(), name='solicitud-detail'),
    
    # ==========================================
    # RESERVACIONES
    # ==========================================
    path('reservaciones/', ReservacionClienteListView.as_view(), name='reservaciones-list'),
    path('reservaciones/<int:pk>/', ReservacionClienteDetailView.as_view(), name='reservacion-detail'),
    path('reservaciones/<int:pk>/cancelar/', CancelarReservacionView.as_view(), name='cancelar-reservacion'),
    
    # ==========================================
    # SEGUIMIENTO
    # ==========================================
    path('reservaciones/<int:reservacion_id>/servicios/', ServiciosReservacionView.as_view(), name='servicios-reservacion'),
    path('servicios/<int:servicio_id>/progreso/', ProgresoServicioView.as_view(), name='progreso-servicio'),
]