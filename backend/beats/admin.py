from django.contrib import admin
from django.utils.html import format_html
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Beat, License, BeatTrack,DraftBeat

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
    list_display = ('title', 'main_artist', 'display_co_artists', 'cheapest_license', "main_track", "duration", 'is_public', 'is_sold', 'created_at')
    list_filter = ('is_public', 'is_sold', 'created_at')
    search_fields = ('title', 'main_artist__username', 'co_artists__username')
    readonly_fields = ('cheapest_license',)
    actions = ['apply_discount', 'mark_as_sold']
    filter_horizontal = ("licenses", "tracks")  # ✅ Permet de gérer les licences et tracks directement dans l'admin

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

    def toggle_visibility(self, request, queryset):
        """Action admin pour rendre les beats publics ou privés."""
        for beat in queryset:
            beat.is_public = not beat.is_public
            beat.save()
        self.message_user(request, "La visibilité des beats sélectionnés a été mise à jour.")
    toggle_visibility.short_description = "Basculer visibilité (public/privé)"


@admin.register(BeatTrack)
class BeatTrackAdmin(admin.ModelAdmin):
    list_display = ("title", "get_beats", "duration", "audio_file")

    def get_beats(self, obj):
        return ", ".join([beat.title for beat in obj.beat.all()])
    get_beats.short_description = "Beats associés"

    

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
    list_display = ('title', 'user', 'bpm', 'key', 'genre', 'is_public', 'created_at', 'updated_at',"audio_file")
    list_filter = ('is_public', 'created_at', 'updated_at', 'user')
    search_fields = ('title', 'user__username', 'genre', 'bpm')
    filter_horizontal = ('licenses', 'tracks', 'co_artists')
    readonly_fields = ('created_at', 'updated_at')

    # Pour afficher l'image de couverture dans l'admin
    def cover_image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{url}" width="100" />', url=obj.cover_image.url)
        return "No image"
    cover_image_preview.short_description = 'Cover Image'

    # Permet d'afficher l'image de couverture dans la liste
    list_display = ('title', 'user', 'bpm', 'key', 'cover_image_preview',"audio_file", 'is_public', 'created_at', 'updated_at')

    # Personnaliser le formulaire d'édition si nécessaire
    fieldsets = (
        (None, {
            'fields': ('title', 'user', 'bpm', 'key', 'genre', 'cover_image',"audio_file", 'is_public', 'co_artists', 'licenses', 'tracks')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

# Enregistrer le modèle et l'admin
admin.site.register(DraftBeat, DraftBeatAdmin)