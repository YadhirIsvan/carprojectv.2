from rest_framework import permissions


class IsCliente(permissions.BasePermission):
    """
    Permiso para usuarios tipo CLIENTE
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.id_tipo.cve == 'CLIENTE'
        )


class IsAsistente(permissions.BasePermission):
    """
    Permiso para usuarios tipo ASISTENTE
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.id_tipo.cve == 'ASISTENTE'
        )


class IsTaller(permissions.BasePermission):
    """
    Permiso para usuarios tipo TALLER (técnicos/mecánicos)
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.id_tipo.cve == 'TALLER'
        )


class IsClienteOrAsistente(permissions.BasePermission):
    """
    Permiso para CLIENTE o ASISTENTE
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.id_tipo.cve in ['CLIENTE', 'ASISTENTE']
        )


class IsAsistenteOrTaller(permissions.BasePermission):
    """
    Permiso para ASISTENTE o TALLER
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.id_tipo.cve in ['ASISTENTE', 'TALLER']
        )