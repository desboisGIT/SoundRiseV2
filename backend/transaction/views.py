from django.shortcuts import render
import logging
import stripe
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Vendor
from .models import Cart,CartItem
from beats.models import License
from decimal import Decimal
from django.shortcuts import get_object_or_404

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_stripe_express_account(request):
    user = request.user

    try:
        # Vérifier si un compte Stripe existe déjà
        vendor, created = Vendor.objects.get_or_create(user=user)

        if vendor.stripe_account_id:
            return Response({"message": "Compte Stripe déjà existant", "stripe_account_id": vendor.stripe_account_id})

        # Créer un compte Stripe Express
        account = stripe.Account.create(
            type="express",
            country="FR",  # À adapter selon le besoin
            email=user.email,
            capabilities={
                "transfers": {"requested": True},
                "card_payments": {"requested": True}
            }
        )

        # Sauvegarde de l'ID Stripe
        vendor.stripe_account_id = account.id
        vendor.save()

        logger.info(f"Compte Stripe créé avec succès pour {user.email} (ID: {account.id})")

        return Response({"message": "Compte Stripe Express créé", "stripe_account_id": account.id})

    except stripe.error.StripeError as e:
        logger.error(f"Erreur Stripe lors de la création du compte : {str(e)}")
        return Response({"error": "Erreur Stripe : " + str(e)}, status=400)

    except Exception as e:
        logger.exception(f"Erreur inattendue lors de la création du compte Stripe : {str(e)}")
        return Response({"error": "Une erreur est survenue"}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stripe_onboarding_link(request):
    user = request.user

    try:
        vendor = Vendor.objects.get(user=user)

        if not vendor.stripe_account_id:
            return Response({"error": "Aucun compte Stripe associé à cet utilisateur"}, status=404)

        # Génération du lien d'onboarding
        link = stripe.AccountLink.create(
            account=vendor.stripe_account_id,
            refresh_url="https://soundrise.com/retry-onboarding",  # Configurable
            return_url="https://soundrise.com/dashboard",  # Configurable
            type="account_onboarding"
        )

        logger.info(f"Lien d'onboarding généré pour {user.email}")

        return Response({"onboarding_url": link.url})

    except Vendor.DoesNotExist:
        return Response({"error": "Compte vendeur introuvable"}, status=404)

    except stripe.error.StripeError as e:
        logger.error(f"Erreur Stripe lors de la génération du lien d'onboarding : {str(e)}")
        return Response({"error": "Erreur Stripe : " + str(e)}, status=400)

    except Exception as e:
        logger.exception(f"Erreur inattendue lors de la génération du lien d'onboarding : {str(e)}")
        return Response({"error": "Une erreur est survenue"}, status=500)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_stripe_requirements(request):
    user = request.user
    vendor = Vendor.objects.get(user=user)

    try:
        account = stripe.Account.retrieve(vendor.stripe_account_id)

        return Response({
            "charges_enabled": account.charges_enabled,  # Peut encaisser des paiements ?
            "payouts_enabled": account.payouts_enabled,  # Peut recevoir des retraits ?
            "details_submitted": account.details_submitted,  # A fini l'Onboarding ?
            "requirements": account.requirements.currently_due  # Infos manquantes
        })

    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=400)



stripe.api_key = settings.STRIPE_SECRET_KEY

PLATFORM_FEE_PERCENTAGE = 0.05  # 5% frais de plateforme
STRIPE_PERCENTAGE = 0.029  # 2.9% de frais Stripe
STRIPE_FIXED_FEE = 0.30  # 0.30€ de frais fixes



def calculate_final_price(net_price):
    final_price = (net_price + Decimal(STRIPE_FIXED_FEE)) / (Decimal(1) - Decimal(STRIPE_PERCENTAGE) - Decimal(PLATFORM_FEE_PERCENTAGE))
    return round(final_price,2)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """ Création d'une session Stripe avec les prix ajustés """
    user = request.user
    cart = Cart.objects.get(user=user)

    line_items = []
    for item in cart.items.all():
        net_price = item.license.price  # Prix défini par le vendeur
        final_price = calculate_final_price(net_price)  # Prix ajusté avec les frais
        
        line_items.append({
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": item.license.title,
                },
                "unit_amount": int(final_price * 100),  # Convertir en centimes
            },
            
        })

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url="https://soundrise.com/success",
            cancel_url="https://soundrise.com/cancel",
        )

        return Response({"checkout_url": session.url})

    except Exception as e:
        return Response({"error": str(e)}, status=400)
    


####################################### Cart ###################################################

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    """ Récupérer le contenu du panier """
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()

    data = {
        "total_price": cart.total_price,
        "final_price": calculate_final_price(cart.total_price),

        "items": [
            {   "license_user":item.license.user.username,
                "license_id": item.license.id,
                "license_title": item.license.title,
                "price": item.license.price
            }
            for item in cart_items
        ],
    }
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """ Ajouter une licence au panier (sans duplication) """
    user = request.user
    license_id = request.data.get("license_id")

    license = get_object_or_404(License, id=license_id)
    cart, created = Cart.objects.get_or_create(user=user)

    # Vérifier si la licence est déjà dans le panier
    if CartItem.objects.filter(cart=cart, license=license).exists():
        return Response({"message": "Cette licence est déjà dans votre panier."}, status=400)

    CartItem.objects.create(cart=cart, license=license)

    return Response({"message": "Licence ajoutée au panier"})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    """ Supprimer une licence du panier """
    user = request.user
    cart = get_object_or_404(Cart, user=user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    cart_item.delete()
    return Response({"message": "Licence retirée du panier"})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """ Vider entièrement le panier """
    user = request.user
    cart = get_object_or_404(Cart, user=user)
    cart.items.all().delete()
    return Response({"message": "Panier vidé"})