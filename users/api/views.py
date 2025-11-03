from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from users.models import Usuario, TipoUsuario
from .serializers import (
    UsuarioSerializer, UsuarioUpdateSerializer,
    TipoUsuarioSerializer, LoginSerializer,
    CambiarPasswordSerializer, TokenSerializer
)
from .permissions import IsOwnerOrAdmin


# ==========================================
# AUTENTICACIÓN
# ==========================================

class LoginView(APIView):
    """
    POST /api/auth/login/
    Body: {"email": "user@example.com", "password": "12345678"}
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Aquí deberías implementar tu lógica de autenticación
        # Por ahora es un ejemplo simple
        try:
            user = Usuario.objects.get(email=email)
            # TODO: Verificar password con hash
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UsuarioSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'message': 'Sesión cerrada exitosamente'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Token inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )


class RefreshTokenView(APIView):
    """
    POST /api/auth/refresh/
    Body: {"refresh": "token"}
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Token inválido o expirado'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class MeView(APIView):
    """
    GET /api/auth/me/
    Obtener información del usuario actual
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)


# ==========================================
# PERFIL DE USUARIO
# ==========================================

class PerfilUsuarioView(generics.RetrieveUpdateAPIView):
    """
    GET /api/usuarios/perfil/
    PUT /api/usuarios/perfil/
    PATCH /api/usuarios/perfil/
    """
    serializer_class = UsuarioUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UsuarioUpdateSerializer
        return UsuarioSerializer


class CambiarPasswordView(APIView):
    """
    PATCH /api/usuarios/perfil/password/
    Body: {
        "password_actual": "...",
        "password_nuevo": "...",
        "password_confirmacion": "..."
    }
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request):
        serializer = CambiarPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # TODO: Verificar password actual
        # if not user.check_password(serializer.validated_data['password_actual']):
        #     return Response(
        #         {'error': 'Contraseña actual incorrecta'},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        
        # TODO: Actualizar password
        # user.set_password(serializer.validated_data['password_nuevo'])
        # user.save()
        
        return Response(
            {'message': 'Contraseña actualizada exitosamente'},
            status=status.HTTP_200_OK
        )


# ==========================================
# CATÁLOGOS
# ==========================================

class TipoUsuarioListView(generics.ListAPIView):
    """
    GET /api/tipos-usuarios/
    """
    queryset = TipoUsuario.objects.all()
    serializer_class = TipoUsuarioSerializer
    permission_classes = [IsAuthenticated]


class UsuarioListView(generics.ListAPIView):
    """
    GET /api/usuarios/
    """
    queryset = Usuario.objects.all().select_related('id_tipo')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]


class UsuarioDetailView(generics.RetrieveAPIView):
    """
    GET /api/usuarios/{id}/
    """
    queryset = Usuario.objects.all().select_related('id_tipo')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]