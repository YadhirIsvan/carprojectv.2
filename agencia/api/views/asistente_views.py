from users.api.serializers import UsuarioSerializer  # 🔧 Correcto
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from agencia.models import (
    Solicitud, DetalleSolicitud, Reservacion,
    ServicioReservado, Vehiculo, DisponibilidadHorario
)
from users.models import Usuario, TipoUsuario
from ..serializers import (
    SolicitudSerializer, SolicitudCreateSerializer,
    DetalleSolicitudSerializer, ReservacionSerializer,
    ReservacionCreateSerializer, ServicioReservadoSerializer,
    VehiculoSerializer,
    DisponibilidadHorarioSerializer,
    DisponibilidadHorarioCreateSerializer,
    ReservacionConHorarioSerializer,
    ReservacionCreateConHorarioSerializer,
)
from users.api.serializers import UsuarioSerializer  # 🔧 Importar desde users
from ..permissions import IsAsistente
from datetime import datetime, timedelta

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
    

# ==========================================
# DISPONIBILIDAD DE HORARIOS
# ==========================================

class DisponibilidadHorarioListCreateView(generics.ListCreateAPIView):
    """
    GET /api/asistente/disponibilidad/
    POST /api/asistente/disponibilidad/
    
    Listar y crear horarios disponibles
    Filtros: ?fecha=2025-11-10&estado=disponible
    """
    permission_classes = [IsAuthenticated, IsAsistente]
    
    def get_queryset(self):
        queryset = DisponibilidadHorario.objects.all()
        
        # Filtros opcionales
        fecha = self.request.query_params.get('fecha')
        estado = self.request.query_params.get('estado')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        if estado:
            queryset = queryset.filter(estado=estado)
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DisponibilidadHorarioCreateSerializer
        return DisponibilidadHorarioSerializer
    
    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)


class DisponibilidadHorarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/asistente/disponibilidad/{id}/
    PUT /api/asistente/disponibilidad/{id}/
    DELETE /api/asistente/disponibilidad/{id}/
    """
    queryset = DisponibilidadHorario.objects.all()
    serializer_class = DisponibilidadHorarioSerializer
    permission_classes = [IsAuthenticated, IsAsistente]


class CrearHorariosMultiplesView(APIView):
    """
    POST /api/asistente/disponibilidad/crear-multiples/
    
    Crear múltiples horarios de una vez (útil para configurar una semana)
    
    Body: {
        "fecha_inicio": "2025-11-10",
        "fecha_fin": "2025-11-17",
        "dias_semana": [0, 1, 2, 3, 4],  // Lunes a Viernes (0=Lunes, 6=Domingo)
        "horarios": [
            {"hora_inicio": "09:00", "hora_fin": "10:00", "capacidad": 2},
            {"hora_inicio": "10:00", "hora_fin": "11:00", "capacidad": 2},
            {"hora_inicio": "11:00", "hora_fin": "12:00", "capacidad": 2},
            {"hora_inicio": "14:00", "hora_fin": "15:00", "capacidad": 2},
            {"hora_inicio": "15:00", "hora_fin": "16:00", "capacidad": 2}
        ]
    }
    """
    permission_classes = [IsAuthenticated, IsAsistente]
    
    def post(self, request):
        fecha_inicio_str = request.data.get('fecha_inicio')
        fecha_fin_str = request.data.get('fecha_fin')
        dias_semana = request.data.get('dias_semana', [0, 1, 2, 3, 4])  # Default: Lun-Vie
        horarios = request.data.get('horarios', [])
        
        if not all([fecha_inicio_str, fecha_fin_str, horarios]):
            return Response(
                {'error': 'Se requieren fecha_inicio, fecha_fin y horarios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        horarios_creados = []
        fecha_actual = fecha_inicio
        
        while fecha_actual <= fecha_fin:
            # Solo crear si el día está en la lista de días de la semana
            if fecha_actual.weekday() in dias_semana:
                for horario in horarios:
                    try:
                        hora_inicio = datetime.strptime(horario['hora_inicio'], '%H:%M').time()
                        hora_fin = datetime.strptime(horario['hora_fin'], '%H:%M').time()
                        capacidad = horario.get('capacidad', 1)
                        
                        # Verificar si ya existe
                        existe = DisponibilidadHorario.objects.filter(
                            fecha=fecha_actual,
                            hora_inicio=hora_inicio,
                            hora_fin=hora_fin
                        ).exists()
                        
                        if not existe:
                            nuevo_horario = DisponibilidadHorario.objects.create(
                                fecha=fecha_actual,
                                hora_inicio=hora_inicio,
                                hora_fin=hora_fin,
                                capacidad=capacidad,
                                creado_por=request.user
                            )
                            horarios_creados.append(nuevo_horario)
                    
                    except (KeyError, ValueError) as e:
                        continue
            
            fecha_actual += timedelta(days=1)
        
        serializer = DisponibilidadHorarioSerializer(horarios_creados, many=True)
        return Response({
            'message': f'{len(horarios_creados)} horarios creados exitosamente',
            'horarios': serializer.data
        }, status=status.HTTP_201_CREATED)


class BloquearHorarioView(APIView):
    """
    PUT /api/asistente/disponibilidad/{id}/bloquear/
    
    Bloquear un horario (para mantenimiento, días festivos, etc)
    """
    permission_classes = [IsAuthenticated, IsAsistente]
    
    def put(self, request, pk):
        horario = get_object_or_404(DisponibilidadHorario, pk=pk)
        
        if horario.reservaciones_actuales > 0:
            return Response(
                {'error': 'No se puede bloquear un horario que tiene reservaciones'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        horario.estado = 'bloqueado'
        horario.save()
        
        serializer = DisponibilidadHorarioSerializer(horario)
        return Response(serializer.data)


class LiberarHorarioView(APIView):
    """
    PUT /api/asistente/disponibilidad/{id}/liberar/
    
    Liberar un horario bloqueado
    """
    permission_classes = [IsAuthenticated, IsAsistente]
    
    def put(self, request, pk):
        horario = get_object_or_404(DisponibilidadHorario, pk=pk)
        
        horario.estado = 'disponible'
        horario.save()
        
        serializer = DisponibilidadHorarioSerializer(horario)
        return Response(serializer.data)


# ==========================================
# ACTUALIZAR RESERVACIONES (usar nuevo sistema)
# ==========================================

class ReservacionAsistenteListCreateView(generics.ListCreateAPIView):
    """
    GET /api/asistente/reservaciones/
    POST /api/asistente/reservaciones/
    
    🆕 Ahora usa horarios disponibles
    """
    queryset = Reservacion.objects.all().select_related(
        'id_solicitud', 'id_solicitud__id_vehiculo', 'horario'
    ).order_by('-creado_at')
    permission_classes = [IsAuthenticated, IsAsistente]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReservacionCreateConHorarioSerializer
        return ReservacionConHorarioSerializer