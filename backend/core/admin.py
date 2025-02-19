from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser,Report

class CustomUserAdmin(UserAdmin):
    """Configuration de l'affichage du modèle CustomUser dans l'admin Django"""

    model = CustomUser

    list_display = ("id", "email", "username","profile_picture", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active")
    ordering = ("date_joined",)
    search_fields = ("email", "username")

    fieldsets = (
        (_("Informations personnelles"), {"fields": ("email", "username", "password","profile_picture","bio" )}),
                                                    
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


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "reporter", "report_type", "reported_user", "reported_beat", "reason", "created_at")
    list_filter = ("report_type", "reason", "created_at")
    search_fields = ("reporter__username", "reported_user__username", "reported_beat__title", "reason")
    ordering = ("-created_at",)

    def get_readonly_fields(self, request, obj=None):
        """Empêche la modification des champs critiques après création."""
        if obj:  # Si l'objet existe déjà (édition)
            return ["reporter", "report_type", "reported_user", "reported_beat", "created_at"]
        return []
