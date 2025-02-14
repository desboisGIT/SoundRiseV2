
from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "content_preview", "timestamp")
    list_filter = ("timestamp", "sender", "receiver")
    search_fields = ("sender__username", "receiver__username", "content")
    ordering = ("-timestamp",)
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    
    content_preview.short_description = "Aperçu du Message"
