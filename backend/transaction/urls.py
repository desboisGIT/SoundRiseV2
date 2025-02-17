from django.urls import path
from . import views

urlpatterns = [
    path('stripe/create-account/', views.create_stripe_express_account, name='create_stripe_express_account'),
    path('stripe/onboarding-link/', views.get_stripe_onboarding_link, name='get_stripe_onboarding_link'),
    path('stripe/account-requirements/', views.check_stripe_requirements, name='check_stripe_requirements'),

    #Cart 
    
    path('cart/', views.get_cart, name='get_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),

]
