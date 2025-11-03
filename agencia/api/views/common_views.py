from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from agencia.models import Marca, Modelo, ServicioTaller
from ..serializers import MarcaSerializer, ModeloSerializer, ServicioTallerSerializer


class MarcaListView(generics.ListAPIView):
    """
    GET /api/marcas/
    Listar todas las marcas disponibles
    """
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [IsAuthenticated]


class ModelosPorMarcaView(generics.ListAPIView):
    """
    GET /api/marcas/{id}/modelos/
    Listar modelos de una marca específica
    """
    serializer_class = ModeloSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        marca_id = self.kwargs.get('pk')
        return Modelo.objects.filter(id_marca_id=marca_id)


class ServicioTallerListView(generics.ListAPIView):
    """
    GET /api/servicios-taller/
    Listar todos los servicios que ofrece el taller
    """
    queryset = ServicioTaller.objects.filter(activo=True)
    serializer_class = ServicioTallerSerializer
    permission_classes = [IsAuthenticated]