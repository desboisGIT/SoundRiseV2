from django.contrib import admin
from django.utils.html import format_html
from .models import Beat, License

# ✅ Inline pour gérer les licences directement dans l'admin du Beat
class LicenseInline(admin.TabularInline):  
    model = License
    extra = 1  # Nombre de licences vides affichées par défaut
    fields = ('title', 'price', 'license_file', 'is_exclusive')
    readonly_fields = ('final_price',)

    def final_price(self, obj):
        """Retourne le prix final avec la promo appliquée."""
        if obj.promo_percentage:
            discount = obj.price * (obj.promo_percentage / 100)
            return obj.price - discount  # Retourne un float ou Decimal
        return obj.price  # Retourne un float ou Decimal

    final_price.short_description = "Prix Final"
    final_price.admin_order_field = "price"  # Permet de trier la colonne correctement




# ✅ Personnalisation de l'affichage du Beat
@admin.register(Beat)
class BeatAdmin(admin.ModelAdmin):
    list_display = ('title', 'main_artist', 'display_co_artists', 'cheapest_license', 'is_public', 'is_sold', 'created_at')
    list_filter = ('is_public', 'is_sold', 'created_at', 'licenses__price')
    search_fields = ('title', 'main_artist__username', 'co_artists__username')
    inlines = [LicenseInline]
    readonly_fields = ('cheapest_license',)
    actions = ['apply_discount', 'mark_as_sold']

    def display_co_artists(self, obj):
        """Affiche les co-artistes sous forme de liste séparée par des virgules."""
        return ", ".join([artist.username for artist in obj.co_artists.all()])
    display_co_artists.short_description = "Co-artistes"

    def cheapest_license(self, obj):
        """Retourne le prix de la licence la moins chère."""
        cheapest = obj.licenses.order_by('price').first()
        return cheapest.price if cheapest else None  # Retourner None si aucune licence
    cheapest_license.short_description = "Prix Minimum"
    cheapest_license.admin_order_field = "licenses__price"  # Permet de trier la colonne correctement


    def apply_discount(self, request, queryset):
        """Action admin pour appliquer une promo de 10 sur plusieurs beats."""
        for beat in queryset:
            for license in beat.licenses.all():
                license.promo_percentage = 10
                license.save()
        self.message_user(request, "Une réduction de 10 a été appliquée aux beats sélectionnés.")
    apply_discount.short_description = "Appliquer -10 de promo"

    def mark_as_sold(self, request, queryset):
        """Action admin pour marquer des beats comme vendus (exclusifs)."""
        queryset.update(is_sold=True)
        self.message_user(request, "Les beats sélectionnés ont été marqués comme vendus.")
    mark_as_sold.short_description = "Marquer comme vendu (exclusif)"
