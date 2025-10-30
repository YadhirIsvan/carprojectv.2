from rest_framework import viewsets
from agencia.models import *

from .serializers import (
    UsuarioSerializer, TipoUsuarioSerializer, SolicitudSerializer, VehiculoSerializer,
    MarcaSerializer, ModeloSerializer, PropietarioSerializer, ReservacionSerializer,
    ServicioTallerSerializer, ServicioReservadoSerializer, ProgresoServicioSerializer,
    DetalleSolicitudSerializer
)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.all()
    serializer_class = UsuarioSerializer

class TipoUsuarioViewSet(viewsets.ModelViewSet):
    queryset = TiposUsuarios.objects.all()
    serializer_class = TipoUsuarioSerializer

class SolicitudViewSet(viewsets.ModelViewSet):
    queryset = Solicitudes.objects.all()
    serializer_class = SolicitudSerializer

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculos.objects.all()
    serializer_class = VehiculoSerializer

class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marcas.objects.all()
    serializer_class = MarcaSerializer

class ModeloViewSet(viewsets.ModelViewSet):
    queryset = Modelos.objects.all()
    serializer_class = ModeloSerializer

class PropietarioViewSet(viewsets.ModelViewSet):
    queryset = Propietarios.objects.all()
    serializer_class = PropietarioSerializer

class ReservacionViewSet(viewsets.ModelViewSet):
    queryset = Reservaciones.objects.all()
    serializer_class = ReservacionSerializer

class ServicioTallerViewSet(viewsets.ModelViewSet):
    queryset = ServiciosTaller.objects.all()
    serializer_class = ServicioTallerSerializer

class ServicioReservadoViewSet(viewsets.ModelViewSet):
    queryset = ServiciosReservados.objects.all()
    serializer_class = ServicioReservadoSerializer

class ProgresoServicioViewSet(viewsets.ModelViewSet):
    queryset = ProgresoServicio.objects.all()
    serializer_class = ProgresoServicioSerializer

class DetalleSolicitudViewSet(viewsets.ModelViewSet):
    queryset = DetalleSolicitud.objects.all()
    serializer_class = DetalleSolicitudSerializer
