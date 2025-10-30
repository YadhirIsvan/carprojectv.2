from rest_framework import serializers
from agencia.models import *

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = '__all__'

class TipoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposUsuarios
        fields = '__all__'

class SolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solicitudes
        fields = '__all__'

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculos
        fields = '__all__'

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marcas
        fields = '__all__'

class ModeloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modelos
        fields = '__all__'

class PropietarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propietarios
        fields = '__all__'

class ReservacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservaciones
        fields = '__all__'

class ServicioTallerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiciosTaller
        fields = '__all__'

class ServicioReservadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiciosReservados
        fields = '__all__'

class ProgresoServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgresoServicio
        fields = '__all__'

class DetalleSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleSolicitud
        fields = '__all__'
