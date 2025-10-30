# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class DetalleSolicitud(models.Model):
    id_detalle = models.BigAutoField(primary_key=True)
    id_solicitud = models.ForeignKey('Solicitudes', models.DO_NOTHING, db_column='id_solicitud', blank=True, null=True)
    id_vehiculo = models.ForeignKey('Vehiculos', models.DO_NOTHING, db_column='id_vehiculo', blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    costo = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    creado_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detalle_solicitud'


class Marcas(models.Model):
    id_marca = models.BigAutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'marcas'


class Modelos(models.Model):
    id_modelo = models.BigAutoField(primary_key=True)
    id_marca = models.ForeignKey(Marcas, models.DO_NOTHING, db_column='id_marca', blank=True, null=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'modelos'


class ProgresoServicio(models.Model):
    id_prog_serv = models.BigAutoField(primary_key=True)
    id_serv_res = models.ForeignKey('ServiciosReservados', models.DO_NOTHING, db_column='id_serv_res')
    fecha = models.DateTimeField(blank=True, null=True)
    porcentaje = models.IntegerField(blank=True, null=True)
    comentario = models.TextField(blank=True, null=True)
    evidencia_url = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'progreso_servicio'


class Propietarios(models.Model):
    id_propietario = models.BigAutoField(primary_key=True)
    cve = models.CharField(max_length=50, blank=True, null=True)
    nombre = models.CharField(max_length=200, blank=True, null=True)
    contacto = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'propietarios'


class Reservaciones(models.Model):
    id_reservacion = models.BigAutoField(primary_key=True)
    id_solicitud = models.ForeignKey('Solicitudes', models.DO_NOTHING, db_column='id_solicitud', blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    id_estado = models.BigIntegerField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    avance_global = models.IntegerField(blank=True, null=True)
    estado_global = models.CharField(max_length=100, blank=True, null=True)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    creado_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reservaciones'


class ServiciosReservados(models.Model):
    id_serv_res = models.BigAutoField(primary_key=True)
    id_reservacion = models.ForeignKey(Reservaciones, models.DO_NOTHING, db_column='id_reservacion')
    id_servicio = models.ForeignKey('ServiciosTaller', models.DO_NOTHING, db_column='id_servicio')
    id_usuario_taller = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario_taller', blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    avance_porcentaje = models.IntegerField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    creado_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'servicios_reservados'


class ServiciosTaller(models.Model):
    id_servicio = models.BigAutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    costo_base = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    duracion_estimada = models.IntegerField(blank=True, null=True)
    activo = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'servicios_taller'


class Solicitudes(models.Model):
    id_solicitud = models.BigAutoField(primary_key=True)
    id_vehiculo = models.ForeignKey('Vehiculos', models.DO_NOTHING, db_column='id_vehiculo', blank=True, null=True)
    id_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    id_estado = models.BigIntegerField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    referencia_externa = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'solicitudes'


class TiposUsuarios(models.Model):
    id_tipo = models.BigAutoField(primary_key=True)
    cve = models.CharField(unique=True, max_length=20)
    descripcion = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'tipos_usuarios'


class Usuarios(models.Model):
    id_usuario = models.BigAutoField(primary_key=True)
    cve = models.CharField(unique=True, max_length=50, blank=True, null=True)
    id_tipo = models.ForeignKey(TiposUsuarios, models.DO_NOTHING, db_column='id_tipo', blank=True, null=True)
    nombre = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    creado_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuarios'


class Vehiculos(models.Model):
    id_vehiculo = models.BigAutoField(primary_key=True)
    placa = models.CharField(unique=True, max_length=50, blank=True, null=True)
    id_modelo = models.ForeignKey(Modelos, models.DO_NOTHING, db_column='id_modelo', blank=True, null=True)
    id_propietario = models.ForeignKey(Propietarios, models.DO_NOTHING, db_column='id_propietario', blank=True, null=True)
    ano = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    creado_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vehiculos'
