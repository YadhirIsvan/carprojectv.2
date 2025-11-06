from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from agencia.models import (
    Vehiculo, Solicitud, Reservacion, 
    ServicioReservado, ProgresoServicio, DisponibilidadHorario
)
from ..serializers import (
    VehiculoSerializer, VehiculoCreateSerializer,
    SolicitudSerializer, SolicitudCreateSerializer,
    ReservacionSerializer, ServicioReservadoSerializer,
    ProgresoServicioSerializer, DisponibilidadHorarioSerializer,
    ReservacionConHorarioSerializer
)
from ..permissions import IsCliente


# ==========================================
# VEHÍCULOS
# ==========================================

class VehiculoClienteListCreateView(generics.ListCreateAPIView):
    """
    GET /api/cliente/vehiculos/
    POST /api/cliente/vehiculos/
    """
    permission_classes = [IsAuthenticated, IsCliente]
    
    def get_queryset(self):
        # Solo los vehículos del cliente actual
        return Vehiculo.objects.filter(id_usuario_propietario=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VehiculoCreateSerializer
        return VehiculoSerializer
    
    def perform_create(self, serializer):
        # Asignar automáticamente el propietario
        serializer.save(id_usuario_propietario=self.request.user)


class VehiculoClienteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/cliente/vehiculos/{id}/
    PUT /api/cliente/vehiculos/{id}/
    PATCH /api/cliente/vehiculos/{id}/
    DELETE /api/cliente/vehiculos/{id}/
    """
    serializer_class = VehiculoSerializer
    permission_classes = [IsAuthenticated, IsCliente]
    
    def get_queryset(self):
        # Solo puede ver/editar sus propios vehículos
        return Vehiculo.objects.filter(id_usuario_propietario=self.request.user)


# ==========================================
# SOLICITUDES
# ==========================================

class SolicitudClienteListCreateView(generics.ListCreateAPIView):
    """
    GET /api/cliente/solicitudes/
    POST /api/cliente/solicitudes/
    """
    permission_classes = [IsAuthenticated, IsCliente]
    
    def get_queryset(self):
        # Solicitudes del cliente actual
        return Solicitud.objects.filter(id_usuario=self.request.user).select_related(
            'id_vehiculo', 'id_vehiculo__id_modelo', 'id_vehiculo__id_modelo__id_marca'
        ).prefetch_related('detalles', 'reservaciones')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SolicitudCreateSerializer
        return SolicitudSerializer
    
    def perform_create(self, serializer):
        # Asignar automáticamente el usuario
        serializer.save(id_usuario=self.request.user)


class SolicitudClienteDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/cliente/solicitudes/{id}/
    PUT /api/cliente/solicitudes/{id}/
    PATCH /api/cliente/solicitudes/{id}/
    """
    serializer_class = SolicitudSerializer
    permission_classes = [IsAuthenticated, IsCliente]
    
    def get_queryset(self):
        return Solicitud.objects.filter(id_usuario=self.request.user).select_related(
            'id_vehiculo', 'id_vehiculo__id_modelo'
        ).prefetch_related('detalles', 'reservaciones')


# ==========================================
# RESERVACIONES
# ==========================================

class ReservacionClienteListView(generics.ListAPIView):
    """
    GET /api/cliente/reservaciones/
    """
    serializer_class = ReservacionSerializer
    permission_classes = [IsAuthenticated, IsCliente]
    
    def get_queryset(self):
        # Reservaciones de las solicitudes del cliente
        return Reservacion.objects.filter(
            id_solicitud__id_usuario=self.request.user
        ).select_related('id_solicitud', 'id_solicitud__id_vehiculo').order_by('-fecha')


class ReservacionClienteDetailView(generics.RetrieveAPIView):
    """
    GET /api/cliente/reservaciones/{id}/
    """
    serializer_class = ReservacionSerializer
    permission_classes = [IsAuthenticated, IsCliente]
    
    def get_queryset(self):
        return Reservacion.objects.filter(
            id_solicitud__id_usuario=self.request.user
        ).select_related('id_solicitud').prefetch_related('servicios_reservados')


class CancelarReservacionView(APIView):
    """
    PUT /api/cliente/reservaciones/{id}/cancelar/
    
    🆕 Ahora libera el horario automáticamente
    """
    permission_classes = [IsAuthenticated, IsCliente]
    
    def put(self, request, pk):
        reservacion = get_object_or_404(
            Reservacion, 
            pk=pk, 
            id_solicitud__id_usuario=request.user
        )
        
        if reservacion.estado_global != 'pendiente':
            return Response(
                {'error': 'Solo se pueden cancelar reservaciones pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Liberar horario
        if reservacion.horario:
            reservacion.horario.liberar()
        
        reservacion.estado_global = 'cancelada'
        reservacion.save()
        
        serializer = ReservacionConHorarioSerializer(reservacion)
        return Response(serializer.data)


# ==========================================
# SEGUIMIENTO DE SERVICIOS
# ==========================================

class ServiciosReservacionView(generics.ListAPIView):
    """
    GET /api/cliente/reservaciones/{reservacion_id}/servicios/
    """
    serializer_class = ServicioReservadoSerializer
    permission_classes = [IsAuthenticated, IsCliente]
    
    def get_queryset(self):
        reservacion_id = self.kwargs.get('reservacion_id')
        return ServicioReservado.objects.filter(
            id_reservacion_id=reservacion_id,
            id_reservacion__id_solicitud__id_usuario=self.request.user
        ).select_related('id_servicio', 'id_usuario_taller')


class ProgresoServicioView(generics.ListAPIView):
    """
    GET /api/cliente/servicios/{servicio_id}/progreso/
    """
    serializer_class = ProgresoServicioSerializer
    permission_classes = [IsAuthenticated, IsCliente]
    
    def get_queryset(self):
        servicio_id = self.kwargs.get('servicio_id')
        return ProgresoServicio.objects.filter(
            id_serv_res_id=servicio_id,
            id_serv_res__id_reservacion__id_solicitud__id_usuario=self.request.user
        ).order_by('-fecha')
    
class HorariosDisponiblesView(generics.ListAPIView):
    """
    GET /api/cliente/horarios-disponibles/
    
    Ver horarios disponibles para agendar
    Filtros: ?fecha=2025-11-10&fecha_desde=2025-11-10&fecha_hasta=2025-11-15
    """
    serializer_class = DisponibilidadHorarioSerializer
    permission_classes = [IsAuthenticated, IsCliente]
    
    def get_queryset(self):
        queryset = DisponibilidadHorario.objects.filter(
            estado='disponible',
            fecha__gte=datetime.now().date()  # Solo fechas futuras
        ).filter(
            reservaciones_actuales__lt=models.F('capacidad')  # Que tengan espacio
        )
        
        # Filtros opcionales
        fecha = self.request.query_params.get('fecha')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)
        
        return queryset.order_by('fecha', 'hora_inicio')


