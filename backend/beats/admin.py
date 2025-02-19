from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Beat, License,DraftBeat,CollaborationInvite

# ✅ Inline pour gérer les licences directement dans l'admin du Beat
class LicenseInline(admin.TabularInline):  
    model = License
    extra = 1  
    fields = ('title', 'price', 'license_file', 'is_exclusive')
    readonly_fields = ('final_price',)

    def final_price(self, obj):
        if obj.promo_percentage:
            discount = obj.price * (obj.promo_percentage / 100)
            return obj.price - discount  
        return obj.price  

    final_price.short_description = "Prix Final"
    final_price.admin_order_field = "price"


# ✅ Personnalisation de l'affichage du Beat
@admin.register(Beat)
class BeatAdmin(admin.ModelAdmin):
    list_display = ('title', 'main_artist', 'display_co_artists', 'cheapest_license', "duration", 'is_sold', 'created_at',"audio_file")
    list_filter = ('is_sold', 'created_at')
    search_fields = ('title', 'main_artist__username', 'co_artists__username')
    readonly_fields = ('cheapest_license',)
    actions = ['apply_discount', 'mark_as_sold']
    filter_horizontal = ("licenses",)  # ✅ Permet de gérer les licences directement dans l'admin

    def cheapest_license(self, obj):
        """Retourne le prix de la licence la moins chère associée au beat."""
        cheapest = obj.licenses.order_by('price').first()
        return cheapest.price if cheapest else None
    cheapest_license.short_description = "Prix Minimum"

    def display_co_artists(self, obj):
        """Affiche les co-artistes sous forme de liste séparée par des virgules."""
        return ", ".join([artist.username for artist in obj.co_artists.all()])
    display_co_artists.short_description = "Co-artistes"

    def apply_discount(self, request, queryset):
        """Action admin pour appliquer une promo de 10 pourcent sur plusieurs beats."""
        for beat in queryset:
            for license in beat.licenses.all():
                license.promo_percentage = 10
                license.save()
        self.message_user(request, "Une réduction de 10 pourcent a été appliquée aux beats sélectionnés.")
    apply_discount.short_description = "Appliquer -10 pourcent de promo"

    def mark_as_sold(self, request, queryset):
        """Action admin pour marquer des beats comme vendus (exclusifs)."""
        queryset.update(is_sold=True)
        self.message_user(request, "Les beats sélectionnés ont été marqués comme vendus.")
    mark_as_sold.short_description = "Marquer comme vendu (exclusif)"

    




    

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ("title", "get_beats", "price", "is_exclusive", "created_at")
    list_filter = ("is_exclusive",)
    search_fields = ("title", "beat__title")  # ✅ Recherche par titre de beat
    ordering = ("-created_at",)
    
    def get_beats(self, obj):
        """Affiche les beats associés sous forme de texte."""
        return ", ".join([beat.title for beat in obj.beat.all()])
    get_beats.short_description = "Beats associés"



# ✅ Signal pour mettre à jour automatiquement l'audio principal après sauvegarde d'un Beat
@receiver(post_save, sender=Beat)
def update_beat_audio(sender, instance, **kwargs):
    """
    Appelle la méthode select_best_audio du Beat associé après la sauvegarde d'un Beat.
    """
    instance.select_best_audio()


class DraftBeatAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'bpm', 'key', 'cover_image_preview', 'files_list_preview', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'user')
    search_fields = ('title', 'user__username', 'genre', 'bpm')
    filter_horizontal = ('licenses', 'co_artists')
    readonly_fields = ('created_at', 'updated_at')

    # Display cover image preview
    def cover_image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="100" />', obj.cover_image.url)
        return "No image"
    cover_image_preview.short_description = 'Cover Image'

    # ✅ Display available file links
    def files_list_preview(self, obj):
        file_fields = ['mp3', 'wav', 'flac', 'ogg', 'aac', 'alac', 'zip']
        file_links = []
        
        for field in file_fields:
            file = getattr(obj, field)
            if file:
                file_links.append(f'<a href="{file.url}" target="_blank">{field.upper()}</a>')

        if file_links:
            return mark_safe("<br>".join(file_links))
        return "No files uploaded"
    
    files_list_preview.short_description = "Available Files"

    # Custom Admin Form
    fieldsets = (
        (None, {
            'fields': ('title', 'user', 'bpm', 'key', 'genre', 'cover_image', 'co_artists', 'licenses')
        }),
        ('Uploaded Files', {
            'fields': ('mp3', 'wav', 'flac', 'ogg', 'aac', 'alac', 'zip'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

# Register the model
admin.site.register(DraftBeat, DraftBeatAdmin)



@admin.register(CollaborationInvite)
class CollaborationInviteAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'draftbeat', 'status', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'draftbeat__title', 'status')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at',)

    def accept_invite(self, request, queryset):
        """Action admin pour accepter plusieurs invitations."""
        for invite in queryset:
            invite.accept()
        self.message_user(request, "Les invitations sélectionnées ont été acceptées.")
    accept_invite.short_description = "Accepter les invitations sélectionnées"

    def refuse_invite(self, request, queryset):
        """Action admin pour refuser plusieurs invitations."""
        for invite in queryset:
            invite.refuse()
        self.message_user(request, "Les invitations sélectionnées ont été refusées.")
    refuse_invite.short_description = "Refuser les invitations sélectionnées"

    actions = [accept_invite, refuse_invite]