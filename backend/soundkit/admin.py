from django.contrib import admin
from .models import Sample,Soundkit

# Register your models here.
@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

@admin.register(Soundkit)
class SoundkitAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "created_at")
    list_filter = ("created_at", "creator")
    search_fields = ("title", "creator__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    def file_list(self, obj):
        """Affiche la liste des fichiers ZIP dans l'admin (sans extraction)."""
        return ", ".join(obj.extract_file_list()) if obj.zip_file else "Aucun fichier"
    
    file_list.short_description = "Fichiers ZIP"