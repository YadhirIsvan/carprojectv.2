from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from agencia.models import (
    ServicioReservado, ProgresoServicio, Reservacion
)
from ..serializers import (
    ServicioReservadoSerializer, ProgresoServicioSerializer,
    ReservacionSerializer
)
from ..permissions import IsTaller


# ==========================================
# SERVICIOS ASIGNADOS
# ==========================================

class MisServiciosListView(generics.ListAPIView):
    """
    GET /api/taller/mis-servicios/
    """
    serializer_class = ServicioReservadoSerializer
    permission_classes = [IsAuthenticated, IsTaller]
    
    def get_queryset(self):
        # Solo los servicios asignados al técnico actual
        return ServicioReservado.objects.filter(
            id_usuario_taller=self.request.user
        ).select_related(
            'id_servicio', 'id_reservacion', 'id_reservacion__id_solicitud'
        ).order_by('-creado_at')


class MiServicioDetailView(generics.RetrieveAPIView):
    """
    GET /api/taller/mis-servicios/{id}/
    """
    serializer_class = ServicioReservadoSerializer
    permission_classes = [IsAuthenticated, IsTaller]
    
    def get_queryset(self):
        return ServicioReservado.objects.filter(
            id_usuario_taller=self.request.user
        ).select_related('id_servicio', 'id_reservacion').prefetch_related('progresos')


class CambiarEstadoServicioView(APIView):
    """
    PATCH /api/taller/mis-servicios/{id}/estado/
    Body: {"estado": "en_progreso", "avance_porcentaje": 50}
    """
    permission_classes = [IsAuthenticated, IsTaller]
    
    def patch(self, request, pk):
        servicio = get_object_or_404(
            ServicioReservado, 
            pk=pk, 
            id_usuario_taller=request.user
        )
        
        nuevo_estado = request.data.get('estado')
        avance = request.data.get('avance_porcentaje')
        
        if nuevo_estado:
            servicio.estado = nuevo_estado
        if avance is not None:
            servicio.avance_porcentaje = avance
        
        servicio.save()
        
        serializer = ServicioReservadoSerializer(servicio)
        return Response(serializer.data)


# ==========================================
# PROGRESO DE SERVICIOS
# ==========================================

class CrearProgresoServicioView(generics.CreateAPIView):
    """
    POST /api/taller/servicios/{servicio_id}/progreso/
    Body: {
        "porcentaje": 50,
        "comentario": "Filtro de aceite cambiado",
        "evidencia_url": "https://..."
    }
    """
    serializer_class = ProgresoServicioSerializer
    permission_classes = [IsAuthenticated, IsTaller]
    
    def perform_create(self, serializer):
        servicio_id = self.kwargs.get('servicio_id')
        servicio = get_object_or_404(
            ServicioReservado, 
            pk=servicio_id,
            id_usuario_taller=self.request.user
        )
        
        progreso = serializer.save(id_serv_res=servicio)
        
        # Actualizar el avance del servicio
        servicio.avance_porcentaje = progreso.porcentaje
        if progreso.porcentaje == 100:
            servicio.estado = 'completado'
        elif progreso.porcentaje > 0:
            servicio.estado = 'en_progreso'
        servicio.save()


class ListarProgresoServicioView(generics.ListAPIView):
    """
    GET /api/taller/servicios/{servicio_id}/progreso/listar/
    """
    serializer_class = ProgresoServicioSerializer
    permission_classes = [IsAuthenticated, IsTaller]
    
    def get_queryset(self):
        servicio_id = self.kwargs.get('servicio_id')
        return ProgresoServicio.objects.filter(
            id_serv_res_id=servicio_id,
            id_serv_res__id_usuario_taller=self.request.user
        ).order_by('-fecha')


class ActualizarProgresoServicioView(generics.RetrieveUpdateAPIView):
    """
    GET /api/taller/servicios/{servicio_id}/progreso/{id}/
    PUT /api/taller/servicios/{servicio_id}/progreso/{id}/
    PATCH /api/taller/servicios/{servicio_id}/progreso/{id}/
    """
    serializer_class = ProgresoServicioSerializer
    permission_classes = [IsAuthenticated, IsTaller]
    
    def get_queryset(self):
        servicio_id = self.kwargs.get('servicio_id')
        return ProgresoServicio.objects.filter(
            id_serv_res_id=servicio_id,
            id_serv_res__id_usuario_taller=self.request.user
        )


# ==========================================
# CONSULTAS
# ==========================================

class ReservacionTallerDetailView(generics.RetrieveAPIView):
    """
    GET /api/taller/reservaciones/{id}/
    """
    serializer_class = ReservacionSerializer
    permission_classes = [IsAuthenticated, IsTaller]
    
    def get_queryset(self):
        # Solo reservaciones donde el técnico tiene servicios asignados
        return Reservacion.objects.filter(
            servicios_reservados__id_usuario_taller=self.request.user
        ).distinct().select_related('id_solicitud')


class ServicioDetalleView(generics.RetrieveAPIView):
    """
    GET /api/taller/servicios/{id}/detalle/
    """
    serializer_class = ServicioReservadoSerializer
    permission_classes = [IsAuthenticated, IsTaller]
    
    def get_queryset(self):
        return ServicioReservado.objects.filter(
            id_usuario_taller=self.request.user
        ).select_related(
            'id_servicio', 
            'id_reservacion',
            'id_reservacion__id_solicitud__id_vehiculo'
        ).prefetch_related('progresos')