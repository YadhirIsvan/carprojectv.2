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

class Reservacion(models.Model):
    id_solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='reservaciones')
    fecha = models.DateTimeField(null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)
    id_estado = models.BigIntegerField(null=True, blank=True)
    notas = models.TextField(blank=True, null=True)
    avance_global = models.IntegerField(default=0)
    estado_global = models.CharField(max_length=100, default='pendiente')
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    creado_at = models.DateTimeField(auto_now_add=True)

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
