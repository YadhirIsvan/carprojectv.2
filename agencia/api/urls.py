from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet)
router.register(r'tipos-usuarios', views.TipoUsuarioViewSet)
router.register(r'solicitudes', views.SolicitudViewSet)
router.register(r'vehiculos', views.VehiculoViewSet)
router.register(r'marcas', views.MarcaViewSet)
router.register(r'modelos', views.ModeloViewSet)
router.register(r'propietarios', views.PropietarioViewSet)
router.register(r'reservaciones', views.ReservacionViewSet)
router.register(r'servicios-taller', views.ServicioTallerViewSet)
router.register(r'servicios-reservados', views.ServicioReservadoViewSet)
router.register(r'progreso-servicio', views.ProgresoServicioViewSet)
router.register(r'detalle-solicitud', views.DetalleSolicitudViewSet)

urlpatterns = router.urls  
