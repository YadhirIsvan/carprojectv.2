from rest_framework import serializers
from agencia.models import (
    Marca, Modelo, Vehiculo, Solicitud, DetalleSolicitud,
    Reservacion, ServicioTaller, ServicioReservado, ProgresoServicio, DisponibilidadHorario
)
from users.models import Usuario


# ==========================================
# MARCAS Y MODELOS
# ==========================================

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ['id', 'nombre']


class ModeloSerializer(serializers.ModelSerializer):
    marca = serializers.CharField(source='id_marca.nombre', read_only=True)
    
    class Meta:
        model = Modelo
        fields = ['id', 'id_marca', 'marca', 'nombre']


# ==========================================
# VEHÍCULOS
# ==========================================

class VehiculoSerializer(serializers.ModelSerializer):
    modelo_nombre = serializers.CharField(source='id_modelo.nombre', read_only=True)
    marca_nombre = serializers.CharField(source='id_modelo.id_marca.nombre', read_only=True)
    propietario_nombre = serializers.CharField(source='id_usuario_propietario.nombre', read_only=True)
    propietario_email = serializers.CharField(source='id_usuario_propietario.email', read_only=True)
    
    class Meta:
        model = Vehiculo
        fields = [
            'id', 'placa', 'id_modelo', 'modelo_nombre', 'marca_nombre',
            'id_usuario_propietario', 'propietario_nombre', 'propietario_email',
            'ano', 'color', 'creado_at'
        ]
        read_only_fields = ['id', 'creado_at']


class VehiculoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear vehículos (sin id_usuario_propietario porque se asigna automáticamente)
    """
    class Meta:
        model = Vehiculo
        fields = ['placa', 'id_modelo', 'ano', 'color']
    
    def validate_placa(self, value):
        """Validar que la placa sea única"""
        if Vehiculo.objects.filter(placa=value).exists():
            raise serializers.ValidationError("Ya existe un vehículo con esta placa")
        return value.upper()


# ==========================================
# SOLICITUDES
# ==========================================

class DetalleSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleSolicitud
        fields = ['id', 'id_solicitud', 'observaciones', 'costo', 'creado_at']
        read_only_fields = ['id', 'creado_at']


class SolicitudSerializer(serializers.ModelSerializer):
    vehiculo = VehiculoSerializer(source='id_vehiculo', read_only=True)
    usuario_nombre = serializers.CharField(source='id_usuario.nombre', read_only=True)
    detalles = DetalleSolicitudSerializer(many=True, read_only=True)
    
    # Información de reservación si existe
    tiene_reservacion = serializers.SerializerMethodField()
    reservacion_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Solicitud
        fields = [
            'id', 'id_vehiculo', 'vehiculo', 'id_usuario', 'usuario_nombre',
            'fecha_creacion', 'id_estado', 'descripcion', 'referencia_externa',
            'detalles', 'tiene_reservacion', 'reservacion_info'
        ]
        read_only_fields = ['id', 'fecha_creacion']
    
    def get_tiene_reservacion(self, obj):
        return obj.reservaciones.exists()
    
    def get_reservacion_info(self, obj):
        reservacion = obj.reservaciones.first()
        if reservacion:
            return {
                'id': reservacion.id,
                'fecha': reservacion.fecha,
                'hora': reservacion.hora,
                'estado_global': reservacion.estado_global,
                'avance_global': reservacion.avance_global
            }
        return None


class SolicitudCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear solicitudes
    """
    class Meta:
        model = Solicitud
        fields = ['id_vehiculo', 'descripcion', 'referencia_externa']
    
    def validate_id_vehiculo(self, value):
        """Validar que el vehículo pertenezca al usuario actual"""
        user = self.context['request'].user
        if value.id_usuario_propietario != user:
            raise serializers.ValidationError("Este vehículo no te pertenece")
        return value


# ==========================================
# RESERVACIONES
# ==========================================

class ReservacionSerializer(serializers.ModelSerializer):
    solicitud_info = serializers.SerializerMethodField()
    vehiculo_info = serializers.SerializerMethodField()
    servicios_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservacion
        fields = [
            'id', 'id_solicitud', 'solicitud_info', 'vehiculo_info',
            'fecha', 'hora', 'id_estado', 'notas',
            'avance_global', 'estado_global',
            'fecha_inicio', 'fecha_fin', 'creado_at',
            'servicios_count'
        ]
        read_only_fields = ['id', 'creado_at']
    
    def get_solicitud_info(self, obj):
        return {
            'id': obj.id_solicitud.id,
            'descripcion': obj.id_solicitud.descripcion,
            'usuario': obj.id_solicitud.id_usuario.nombre
        }
    
    def get_vehiculo_info(self, obj):
        vehiculo = obj.id_solicitud.id_vehiculo
        return {
            'placa': vehiculo.placa,
            'modelo': vehiculo.id_modelo.nombre if vehiculo.id_modelo else None,
            'marca': vehiculo.id_modelo.id_marca.nombre if vehiculo.id_modelo else None,
            'color': vehiculo.color
        }
    
    def get_servicios_count(self, obj):
        return obj.servicios_reservados.count()


class ReservacionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear reservaciones
    """
    class Meta:
        model = Reservacion
        fields = [
            'id_solicitud', 'fecha', 'hora', 'notas',
            'fecha_inicio', 'fecha_fin'
        ]
    
    def validate_id_solicitud(self, value):
        """Validar que la solicitud no tenga ya una reservación activa"""
        if value.reservaciones.filter(estado_global__in=['pendiente', 'confirmada', 'en_progreso']).exists():
            raise serializers.ValidationError("Esta solicitud ya tiene una reservación activa")
        return value


# ==========================================
# SERVICIOS TALLER
# ==========================================

class ServicioTallerSerializer(serializers.ModelSerializer):
    duracion_estimada_horas = serializers.SerializerMethodField()
    
    class Meta:
        model = ServicioTaller
        fields = [
            'id', 'nombre', 'descripcion', 'costo_base',
            'duracion_estimada', 'duracion_estimada_horas', 'activo'
        ]
    
    def get_duracion_estimada_horas(self, obj):
        """Convertir minutos a horas para mejor lectura"""
        if obj.duracion_estimada:
            horas = obj.duracion_estimada // 60
            minutos = obj.duracion_estimada % 60
            if horas > 0 and minutos > 0:
                return f"{horas}h {minutos}min"
            elif horas > 0:
                return f"{horas}h"
            else:
                return f"{minutos}min"
        return None


# ==========================================
# SERVICIOS RESERVADOS
# ==========================================

class ServicioReservadoSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(source='id_servicio.nombre', read_only=True)
    servicio_costo = serializers.DecimalField(
        source='id_servicio.costo_base', 
        max_digits=12, 
        decimal_places=2, 
        read_only=True
    )
    tecnico_nombre = serializers.CharField(source='id_usuario_taller.nombre', read_only=True)
    
    # Información de la reservación
    reservacion_fecha = serializers.DateTimeField(source='id_reservacion.fecha', read_only=True)
    reservacion_id = serializers.IntegerField(source='id_reservacion.id', read_only=True)
    
    # Información del vehículo
    vehiculo_info = serializers.SerializerMethodField()
    
    # Progreso
    ultimo_progreso = serializers.SerializerMethodField()
    
    class Meta:
        model = ServicioReservado
        fields = [
            'id', 'id_reservacion', 'reservacion_id', 'reservacion_fecha',
            'id_servicio', 'servicio_nombre', 'servicio_costo',
            'id_usuario_taller', 'tecnico_nombre',
            'estado', 'avance_porcentaje', 'observaciones',
            'fecha_inicio', 'fecha_fin', 'creado_at',
            'vehiculo_info', 'ultimo_progreso'
        ]
        read_only_fields = ['id', 'creado_at']
    
    def get_vehiculo_info(self, obj):
        vehiculo = obj.id_reservacion.id_solicitud.id_vehiculo
        return {
            'placa': vehiculo.placa,
            'modelo': vehiculo.id_modelo.nombre if vehiculo.id_modelo else None,
            'marca': vehiculo.id_modelo.id_marca.nombre if vehiculo.id_modelo else None
        }
    
    def get_ultimo_progreso(self, obj):
        ultimo = obj.progresos.order_by('-fecha').first()
        if ultimo:
            return {
                'fecha': ultimo.fecha,
                'porcentaje': ultimo.porcentaje,
                'comentario': ultimo.comentario
            }
        return None


# ==========================================
# PROGRESO DE SERVICIO
# ==========================================

class ProgresoServicioSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(
        source='id_serv_res.id_servicio.nombre', 
        read_only=True
    )
    
    class Meta:
        model = ProgresoServicio
        fields = [
            'id', 'id_serv_res', 'servicio_nombre',
            'fecha', 'porcentaje', 'comentario', 'evidencia_url'
        ]
        read_only_fields = ['id', 'fecha']
    
    def validate_porcentaje(self, value):
        """Validar que el porcentaje esté entre 0 y 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("El porcentaje debe estar entre 0 y 100")
        return value
    
# agencia/api/serializers.py

class DisponibilidadHorarioSerializer(serializers.ModelSerializer):
    esta_disponible = serializers.BooleanField(read_only=True)
    dia_semana = serializers.SerializerMethodField()
    
    class Meta:
        model = DisponibilidadHorario
        fields = [
            'id', 'fecha', 'hora_inicio', 'hora_fin', 
            'estado', 'capacidad', 'reservaciones_actuales',
            'esta_disponible', 'dia_semana', 'creado_at'
        ]
        read_only_fields = ['id', 'reservaciones_actuales', 'creado_at']
    
    def get_dia_semana(self, obj):
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return dias[obj.fecha.weekday()]


class DisponibilidadHorarioCreateSerializer(serializers.ModelSerializer):
    """
    Para crear múltiples horarios de una vez
    """
    class Meta:
        model = DisponibilidadHorario
        fields = ['fecha', 'hora_inicio', 'hora_fin', 'capacidad', 'estado']
    
    def validate(self, data):
        # Validar que hora_fin > hora_inicio
        if data['hora_fin'] <= data['hora_inicio']:
            raise serializers.ValidationError({
                'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio'
            })
        
        # Validar que no haya solapamiento
        fecha = data['fecha']
        hora_inicio = data['hora_inicio']
        hora_fin = data['hora_fin']
        
        solapamiento = DisponibilidadHorario.objects.filter(
            fecha=fecha,
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio
        )
        
        if solapamiento.exists():
            raise serializers.ValidationError(
                'Ya existe un horario que se solapa con este rango'
            )
        
        return data


class ReservacionConHorarioSerializer(serializers.ModelSerializer):
    """
    Serializer actualizado para reservaciones con horarios
    """
    horario_info = DisponibilidadHorarioSerializer(source='horario', read_only=True)
    solicitud_info = serializers.SerializerMethodField()
    vehiculo_info = serializers.SerializerMethodField()
    servicios_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservacion
        fields = [
            'id', 'id_solicitud', 'horario', 'horario_info',
            'solicitud_info', 'vehiculo_info',
            'notas', 'avance_global', 'estado_global',
            'fecha_inicio', 'fecha_fin', 'creado_at',
            'servicios_count'
        ]
        read_only_fields = ['id', 'creado_at', 'fecha', 'hora']
    
    def get_solicitud_info(self, obj):
        return {
            'id': obj.id_solicitud.id,
            'descripcion': obj.id_solicitud.descripcion,
            'usuario': obj.id_solicitud.id_usuario.nombre
        }
    
    def get_vehiculo_info(self, obj):
        vehiculo = obj.id_solicitud.id_vehiculo
        return {
            'placa': vehiculo.placa,
            'modelo': vehiculo.id_modelo.nombre if vehiculo.id_modelo else None,
            'marca': vehiculo.id_modelo.id_marca.nombre if vehiculo.id_modelo else None,
            'color': vehiculo.color
        }
    
    def get_servicios_count(self, obj):
        return obj.servicios_reservados.count()


class ReservacionCreateConHorarioSerializer(serializers.ModelSerializer):
    """
    Para crear reservación seleccionando un horario disponible
    """
    class Meta:
        model = Reservacion
        fields = ['id_solicitud', 'horario', 'notas']
    
    def validate_horario(self, value):
        if not value.esta_disponible:
            raise serializers.ValidationError(
                'Este horario ya no está disponible'
            )
        return value
    
    def validate_id_solicitud(self, value):
        # Verificar que la solicitud no tenga ya una reservación activa
        if value.reservaciones.filter(
            estado_global__in=['pendiente', 'confirmada', 'en_progreso']
        ).exists():
            raise serializers.ValidationError(
                'Esta solicitud ya tiene una reservación activa'
            )
        return value
    
    def create(self, validated_data):
        horario = validated_data['horario']
        reservacion = Reservacion.objects.create(**validated_data)
        
        # Marcar horario como reservado
        horario.reservar(reservacion)
        
        return reservacion