from users.api.serializers import UsuarioSerializer  # 🔧 Correcto
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from agencia.models import (
    Solicitud, DetalleSolicitud, Reservacion,
    ServicioReservado, Vehiculo
)
from users.models import Usuario, TipoUsuario
from ..serializers import (
    SolicitudSerializer, SolicitudCreateSerializer,
    DetalleSolicitudSerializer, ReservacionSerializer,
    ReservacionCreateSerializer, ServicioReservadoSerializer,
    VehiculoSerializer,
)
from users.api.serializers import UsuarioSerializer  # 🔧 Importar desde users
from ..permissions import IsAsistente

# ... resto del código iguals
# ==========================================
# SOLICITUDES
# ==========================================

class SolicitudAsistenteListView(generics.ListAPIView):
    """
    GET /api/asistente/solicitudes/
    """
    queryset = Solicitud.objects.all().select_related(
        'id_vehiculo', 'id_usuario'
    ).prefetch_related('detalles', 'reservaciones').order_by('-fecha_creacion')
    serializer_class = SolicitudSerializer
    permission_classes = [IsAuthenticated, IsAsistente]


class SolicitudAsistenteDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/asistente/solicitudes/{id}/
    PUT /api/asistente/solicitudes/{id}/
    PATCH /api/asistente/solicitudes/{id}/
    """
    queryset = Solicitud.objects.all().select_related('id_vehiculo', 'id_usuario')
    serializer_class = SolicitudSerializer
    permission_classes = [IsAuthenticated, IsAsistente]


class CambiarEstadoSolicitudView(APIView):
    """
    PATCH /api/asistente/solicitudes/{id}/estado/
    """
    permission_classes = [IsAuthenticated, IsAsistente]
    
    def patch(self, request, pk):
        solicitud = get_object_or_404(Solicitud, pk=pk)
        nuevo_estado = request.data.get('id_estado')
        
        if not nuevo_estado:
            return Response(
                {'error': 'El campo id_estado es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        solicitud.id_estado = nuevo_estado
        solicitud.save()
        
        serializer = SolicitudSerializer(solicitud)
        return Response(serializer.data)


class CrearDetalleSolicitudView(generics.CreateAPIView):
    """
    POST /api/asistente/solicitudes/{solicitud_id}/detalle/
    """
    serializer_class = DetalleSolicitudSerializer
    permission_classes = [IsAuthenticated, IsAsistente]
    
    def perform_create(self, serializer):
        solicitud_id = self.kwargs.get('solicitud_id')
        solicitud = get_object_or_404(Solicitud, pk=solicitud_id)
        serializer.save(id_solicitud=solicitud)


# ==========================================
# RESERVACIONES
# ==========================================

class ReservacionAsistenteListCreateView(generics.ListCreateAPIView):
    """
    GET /api/asistente/reservaciones/
    POST /api/asistente/reservaciones/
    """
    queryset = Reservacion.objects.all().select_related(
        'id_solicitud', 'id_solicitud__id_vehiculo'
    ).order_by('-fecha')
    permission_classes = [IsAuthenticated, IsAsistente]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReservacionCreateSerializer
        return ReservacionSerializer


class ReservacionAsistenteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/asistente/reservaciones/{id}/
    PUT /api/asistente/reservaciones/{id}/
    PATCH /api/asistente/reservaciones/{id}/
    DELETE /api/asistente/reservaciones/{id}/
    """
    queryset = Reservacion.objects.all().select_related('id_solicitud')
    serializer_class = ReservacionSerializer
    permission_classes = [IsAuthenticated, IsAsistente]


class CambiarEstadoReservacionView(APIView):
    """
    PATCH /api/asistente/reservaciones/{id}/estado/
    """
    permission_classes = [IsAuthenticated, IsAsistente]
    
    def patch(self, request, pk):
        reservacion = get_object_or_404(Reservacion, pk=pk)
        nuevo_estado = request.data.get('estado_global')
        
        if not nuevo_estado:
            return Response(
                {'error': 'El campo estado_global es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservacion.estado_global = nuevo_estado
        reservacion.save()
        
        serializer = ReservacionSerializer(reservacion)
        return Response(serializer.data)


# ==========================================
# ASIGNACIÓN DE SERVICIOS
# ==========================================

class AsignarServiciosView(APIView):
    """
    POST /api/asistente/reservaciones/{reservacion_id}/servicios/
    Body: {
        "servicios": [
            {"id_servicio": 1, "id_usuario_taller": 5},
            {"id_servicio": 2, "id_usuario_taller": 6}
        ]
    }
    """
    permission_classes = [IsAuthenticated, IsAsistente]
    
    def post(self, request, reservacion_id):
        reservacion = get_object_or_404(Reservacion, pk=reservacion_id)
        servicios_data = request.data.get('servicios', [])
        
        if not servicios_data:
            return Response(
                {'error': 'Debe proporcionar al menos un servicio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        servicios_creados = []
        for servicio_data in servicios_data:
            servicio_reservado = ServicioReservado.objects.create(
                id_reservacion=reservacion,
                id_servicio_id=servicio_data.get('id_servicio'),
                id_usuario_taller_id=servicio_data.get('id_usuario_taller'),
            )
            servicios_creados.append(servicio_reservado)
        
        serializer = ServicioReservadoSerializer(servicios_creados, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AsignarTecnicoView(APIView):
    """
    PUT /api/asistente/servicios-reservados/{id}/asignar-tecnico/
    """
    permission_classes = [IsAuthenticated, IsAsistente]
    
    def put(self, request, pk):
        servicio_reservado = get_object_or_404(ServicioReservado, pk=pk)
        tecnico_id = request.data.get('id_usuario_taller')
        
        if not tecnico_id:
            return Response(
                {'error': 'El campo id_usuario_taller es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        servicio_reservado.id_usuario_taller_id = tecnico_id
        servicio_reservado.save()
        
        serializer = ServicioReservadoSerializer(servicio_reservado)
        return Response(serializer.data)


class ServiciosReservadosListView(generics.ListAPIView):
    """
    GET /api/asistente/servicios-reservados/
    """
    queryset = ServicioReservado.objects.all().select_related(
        'id_servicio', 'id_usuario_taller', 'id_reservacion'
    ).order_by('-creado_at')
    serializer_class = ServicioReservadoSerializer
    permission_classes = [IsAuthenticated, IsAsistente]


# ==========================================
# CATÁLOGOS Y CONSULTAS
# ==========================================

class ClientesListView(generics.ListAPIView):
    """
    GET /api/asistente/clientes/
    """
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, IsAsistente]
    
    def get_queryset(self):
        tipo_cliente = TipoUsuario.objects.filter(cve='CLIENTE').first()
        if tipo_cliente:
            return Usuario.objects.filter(id_tipo=tipo_cliente)
        return Usuario.objects.none()


class VehiculosListView(generics.ListAPIView):
    """
    GET /api/asistente/vehiculos/
    """
    queryset = Vehiculo.objects.all().select_related(
        'id_modelo', 'id_modelo__id_marca', 'id_usuario_propietario'
    )
    serializer_class = VehiculoSerializer
    permission_classes = [IsAuthenticated, IsAsistente]


class TecnicosListView(generics.ListAPIView):
    """
    GET /api/asistente/tecnicos/
    """
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, IsAsistente]
    
    def get_queryset(self):
        tipo_taller = TipoUsuario.objects.filter(cve='TALLER').first()
        if tipo_taller:
            return Usuario.objects.filter(id_tipo=tipo_taller)
        return Usuario.objects.none()