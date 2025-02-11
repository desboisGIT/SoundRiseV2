
from django.contrib import admin
from .models import Beat

@admin.register(Beat)
class BeatAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "bpm", "genre", "price", "license_type", "created_at")
    list_filter = ("genre", "license_type", "created_at")
    search_fields = ("title", "user__username", "genre")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("likes",)  # Permet une meilleure gestion des likes dans l'admin

    fieldsets = (
        ("Informations principales", {
            "fields": ("user", "title", "audio_file", "cover_image", "bpm", "key", "genre", "price", "license_type")
        }),
        ("Engagement", {
            "fields": ("likes",),
            "classes": ("collapse",),
        }),
        ("Dates", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

