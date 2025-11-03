from django.urls import path
from .views.asistente_views import (
    # Solicitudes
    SolicitudAsistenteListView,
    SolicitudAsistenteDetailView,
    CambiarEstadoSolicitudView,
    CrearDetalleSolicitudView,
    
    # Reservaciones
    ReservacionAsistenteListCreateView,
    ReservacionAsistenteDetailView,
    CambiarEstadoReservacionView,
    
    # Servicios Reservados
    AsignarServiciosView,
    AsignarTecnicoView,
    ServiciosReservadosListView,
    
    # Catálogos y consultas
    ClientesListView,
    VehiculosListView,
    TecnicosListView,
)

app_name = 'asistente'

urlpatterns = [
    # ==========================================
    # SOLICITUDES
    # ==========================================
    path('solicitudes/', SolicitudAsistenteListView.as_view(), name='solicitudes-list'),
    path('solicitudes/<int:pk>/', SolicitudAsistenteDetailView.as_view(), name='solicitud-detail'),
    path('solicitudes/<int:pk>/estado/', CambiarEstadoSolicitudView.as_view(), name='cambiar-estado-solicitud'),
    path('solicitudes/<int:solicitud_id>/detalle/', CrearDetalleSolicitudView.as_view(), name='crear-detalle'),
    
    # ==========================================
    # RESERVACIONES
    # ==========================================
    path('reservaciones/', ReservacionAsistenteListCreateView.as_view(), name='reservaciones-list-create'),
    path('reservaciones/<int:pk>/', ReservacionAsistenteDetailView.as_view(), name='reservacion-detail'),
    path('reservaciones/<int:pk>/estado/', CambiarEstadoReservacionView.as_view(), name='cambiar-estado-reservacion'),
    
    # ==========================================
    # ASIGNACIÓN DE SERVICIOS
    # ==========================================
    path('reservaciones/<int:reservacion_id>/servicios/', AsignarServiciosView.as_view(), name='asignar-servicios'),
    path('servicios-reservados/<int:pk>/asignar-tecnico/', AsignarTecnicoView.as_view(), name='asignar-tecnico'),
    path('servicios-reservados/', ServiciosReservadosListView.as_view(), name='servicios-reservados-list'),
    
    # ==========================================
    # CATÁLOGOS Y CONSULTAS
    # ==========================================
    path('clientes/', ClientesListView.as_view(), name='clientes-list'),
    path('vehiculos/', VehiculosListView.as_view(), name='vehiculos-list'),
    path('tecnicos/', TecnicosListView.as_view(), name='tecnicos-list'),
]