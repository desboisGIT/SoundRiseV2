from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    """
    Seul le propriétaire du Beat ou un admin peut modifier ou supprimer le Beat.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user or request.user.is_staff  # L'utilisateur doit être le propriétaire ou un admin
