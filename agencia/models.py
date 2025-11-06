from django.db import models
from users.models import Usuario  # relación con usuarios

# ========================
# MARCAS Y MODELOS
# ========================

class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Modelo(models.Model):
    id_marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name='modelos')
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.id_marca.nombre} {self.nombre}"


# ========================
# VEHÍCULOS
# ========================

class Vehiculo(models.Model):
    placa = models.CharField(max_length=50, unique=True)
    id_modelo = models.ForeignKey(Modelo, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehiculos')
    id_usuario_propietario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='vehiculos')
    ano = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    creado_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.placa} - {self.id_usuario_propietario.nombre}"


# ========================
# SOLICITUDES Y DETALLES
# ========================

class Solicitud(models.Model):
    id_vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='solicitudes')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes_creadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    id_estado = models.BigIntegerField(null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)
    referencia_externa = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Solicitud {self.id} - {self.id_usuario.nombre}"


class DetalleSolicitud(models.Model):
    id_solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='detalles')
    observaciones = models.TextField(blank=True, null=True)
    costo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    creado_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Detalle de Solicitud {self.id_solicitud.id}"


# ========================
# RESERVACIONES
# ========================
# agencia/models.py

class DisponibilidadHorario(models.Model):
    """
    Horarios disponibles del taller para reservaciones
    """
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('reservado', 'Reservado'),
        ('bloqueado', 'Bloqueado'),  # Para mantenimiento o días festivos
    ]
    
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    capacidad = models.IntegerField(default=1)  # Cuántos autos puede atender simultáneamente
    reservaciones_actuales = models.IntegerField(default=0)
    
    # Relación con reservación (si está ocupado)
    reservacion = models.ForeignKey(
        'Reservacion', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='horario_asignado'
    )
    
    # Metadata
    creado_por = models.ForeignKey(
        'users.Usuario', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='horarios_creados'
    )
    creado_at = models.DateTimeField(auto_now_add=True)
    actualizado_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['fecha', 'hora_inicio']
        unique_together = ['fecha', 'hora_inicio', 'hora_fin']
        verbose_name = 'Disponibilidad de Horario'
        verbose_name_plural = 'Disponibilidades de Horarios'
    
    def __str__(self):
        return f"{self.fecha} {self.hora_inicio}-{self.hora_fin} ({self.estado})"
    
    @property
    def esta_disponible(self):
        """Verifica si el horario está disponible"""
        return (
            self.estado == 'disponible' and 
            self.reservaciones_actuales < self.capacidad
        )
    
    def reservar(self, reservacion):
        """Marca el horario como reservado"""
        if not self.esta_disponible:
            raise ValueError("Este horario no está disponible")
        
        self.reservaciones_actuales += 1
        if self.reservaciones_actuales >= self.capacidad:
            self.estado = 'reservado'
        self.reservacion = reservacion
        self.save()
    
    def liberar(self):
        """Libera el horario cuando se cancela una reservación"""
        if self.reservaciones_actuales > 0:
            self.reservaciones_actuales -= 1
        
        if self.reservaciones_actuales < self.capacidad:
            self.estado = 'disponible'
            self.reservacion = None
        self.save()
        
class Reservacion(models.Model):
    id_solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='reservaciones')
    
    # 🆕 Ahora usa DisponibilidadHorario
    horario = models.ForeignKey(
        DisponibilidadHorario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reservaciones'
    )
    
    # Mantener campos para compatibilidad (opcional)
    fecha = models.DateTimeField(null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)
    
    id_estado = models.BigIntegerField(null=True, blank=True)
    notas = models.TextField(blank=True, null=True)
    avance_global = models.IntegerField(default=0)
    estado_global = models.CharField(max_length=100, default='pendiente')
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    creado_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Auto-sincronizar fecha/hora desde horario
        if self.horario:
            self.fecha = self.horario.fecha
            self.hora = self.horario.hora_inicio
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Reservación {self.id} - {self.id_solicitud.id}"
    
# ========================
# SERVICIOS DEL TALLER
# ========================

class ServicioTaller(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    costo_base = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    duracion_estimada = models.IntegerField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


# ========================
# SERVICIOS RESERVADOS
# ========================

class ServicioReservado(models.Model):
    id_reservacion = models.ForeignKey(Reservacion, on_delete=models.CASCADE, related_name='servicios_reservados')
    id_servicio = models.ForeignKey(ServicioTaller, on_delete=models.CASCADE, related_name='servicios_reservados')
    id_usuario_taller = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='servicios_asignados')
    estado = models.CharField(max_length=100, default='pendiente')
    avance_porcentaje = models.IntegerField(default=0)
    observaciones = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    creado_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id_servicio.nombre} - {self.estado}"


# ========================
# PROGRESO DE SERVICIO
# ========================

class ProgresoServicio(models.Model):
    id_serv_res = models.ForeignKey(ServicioReservado, on_delete=models.CASCADE, related_name='progresos')
    fecha = models.DateTimeField(auto_now_add=True)
    porcentaje = models.IntegerField(null=True, blank=True)
    comentario = models.TextField(blank=True, null=True)
    evidencia_url = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return f"Progreso {self.porcentaje}% del servicio {self.id_serv_res.id}"

