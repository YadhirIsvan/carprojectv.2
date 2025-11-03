from rest_framework import serializers
from users.models import Usuario, TipoUsuario


# ==========================================
# TIPOS DE USUARIO
# ==========================================

class TipoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoUsuario
        fields = ['id', 'cve', 'descripcion']


# ==========================================
# USUARIOS
# ==========================================

class UsuarioSerializer(serializers.ModelSerializer):
    tipo_descripcion = serializers.CharField(source='id_tipo.descripcion', read_only=True)
    tipo_cve = serializers.CharField(source='id_tipo.cve', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'cve', 'id_tipo', 'tipo_cve', 'tipo_descripcion',
            'nombre', 'email', 'telefono', 'creado_at'
        ]
        read_only_fields = ['id', 'creado_at']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear usuarios
    """
    class Meta:
        model = Usuario
        fields = ['cve', 'id_tipo', 'nombre', 'email', 'telefono']
    
    def validate_email(self, value):
        """Validar que el email sea único"""
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email")
        return value.lower()


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar perfil de usuario
    """
    class Meta:
        model = Usuario
        fields = ['nombre', 'telefono']


class CambiarPasswordSerializer(serializers.Serializer):
    """
    Serializer para cambiar contraseña
    """
    password_actual = serializers.CharField(write_only=True, required=True)
    password_nuevo = serializers.CharField(write_only=True, required=True)
    password_confirmacion = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        if attrs['password_nuevo'] != attrs['password_confirmacion']:
            raise serializers.ValidationError({
                "password_confirmacion": "Las contraseñas no coinciden"
            })
        
        if len(attrs['password_nuevo']) < 8:
            raise serializers.ValidationError({
                "password_nuevo": "La contraseña debe tener al menos 8 caracteres"
            })
        
        return attrs


# ==========================================
# AUTENTICACIÓN
# ==========================================

class LoginSerializer(serializers.Serializer):
    """
    Serializer para login
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class TokenSerializer(serializers.Serializer):
    """
    Serializer para respuesta de tokens
    """
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UsuarioSerializer()