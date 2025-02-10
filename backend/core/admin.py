from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """Configuration de l'affichage du modèle CustomUser dans l'admin Django"""

    model = CustomUser

    list_display = ("email", "username", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active")
    ordering = ("date_joined",)
    search_fields = ("email", "username")

    fieldsets = (
        (_("Informations personnelles"), {"fields": ("email", "username", "password")}),
        (_("Permissions"), {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (
            _("Créer un utilisateur"),
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )

    readonly_fields = ("date_joined", "last_login")  # ✅ Rendre `date_joined` et `last_login` en lecture seule

admin.site.register(CustomUser, CustomUserAdmin)
