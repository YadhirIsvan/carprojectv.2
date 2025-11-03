from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# ==========================================
# PRIMERO: TipoUsuario (debe ir antes)
# ==========================================

class TipoUsuario(models.Model):
    cve = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion


# ==========================================
# SEGUNDO: UsuarioManager
# ==========================================

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, id_tipo, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        if not nombre:
            raise ValueError('El nombre es obligatorio')
        if not id_tipo:
            raise ValueError('El tipo de usuario es obligatorio')
        
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, id_tipo=id_tipo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, nombre, password=None, **extra_fields):
        # Obtener o crear tipo de usuario ADMIN
        tipo_admin, created = TipoUsuario.objects.get_or_create(
            cve='ADMIN',
            defaults={'descripcion': 'Administrador'}
        )
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, nombre, tipo_admin, password, **extra_fields)


# ==========================================
# TERCERO: Usuario (ahora TipoUsuario ya existe)
# ==========================================

class Usuario(AbstractBaseUser, PermissionsMixin):
    cve = models.CharField(max_length=50, unique=True, null=True, blank=True)
    id_tipo = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE, related_name='usuarios')
    nombre = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    creado_at = models.DateTimeField(auto_now_add=True)
    
    # Campos requeridos por Django para autenticación
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']  # Campos requeridos además de email y password
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios'
    
    def __str__(self):
        return f"{self.nombre} ({self.email})"
    
    def get_full_name(self):
        return self.nombre
    
    def get_short_name(self):
        return self.nombre.split()[0] if self.nombre else self.email