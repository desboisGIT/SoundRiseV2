from rest_framework.permissions import BasePermission,SAFE_METHODS

class IsOwnerOrAdmin(BasePermission):
    """
    Seul le propriétaire du Beat ou un admin peut modifier ou supprimer le Beat.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user or request.user.is_staff  # L'utilisateur doit être le propriétaire ou un admin


class AllowAnyGetAuthenticatedElse(BasePermission):
    """
    Autorise tout le monde à faire des requêtes GET.
    Exige une authentification pour toutes les autres méthodes.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:  # SAFE_METHODS = ("GET", "HEAD", "OPTIONS")
            return True  # GET est autorisé à tout le monde
        return request.user and request.user.is_authenticated  # Authentification requise pour les autres méthodes
