from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso para que solo el propietario o admin pueda acceder
    """
    def has_object_permission(self, request, view, obj):
        # Admin puede todo
        if request.user.is_staff:
            return True
        
        # El usuario solo puede acceder a su propia información
        return obj == request.user


class IsAuthenticatedUser(permissions.BasePermission):
    """
    Permiso básico para usuarios autenticados
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated