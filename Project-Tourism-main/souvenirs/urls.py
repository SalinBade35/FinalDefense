from django.urls import path
from . import views

app_name = 'souvenirs'

urlpatterns = [
    # Main product listing page
    path('', views.product_list_view, name='souvenir_list'),
    
    # AJAX search for products
    path('ajax-search/', views.ajax_product_search, name='ajax_product_search'),

    # Product detail pages
    path('product-details/', views.static_product_detail_view, name='static_product_detail'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),

    # Cart functionality
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('get-cart-items/', views.get_cart_items, name='get_cart_items'),
    path('remove-cart-item/', views.remove_cart_item, name='remove_cart_item'),
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),

    # Wishlist functionality
    path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('get-wishlist-items/', views.get_wishlist_items, name='get_wishlist_items'),
    path('remove-wishlist-item/', views.remove_wishlist_item, name='remove_wishlist_item'),
    path('wishlist-add-to-cart/', views.wishlist_add_to_cart, name='wishlist_add_to_cart'),

    # Order and delivery
    path('delivery/', views.delivery_view, name='delivery'),
    path('process-delivery-order/', views.process_delivery_order, name='process_delivery_order'),

    # eSewa payment integration
    path("paymentsuccess/<int:order_id>/",views.paymentsuccess,name="paymentsuccess"),
    path('payment-ways/<int:order_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),

    # Reviews
    path('product/<int:product_id>/submit-review/', views.submit_review, name='submit_review'),
    path('product/<int:product_id>/get-reviews/', views.get_reviews, name='get_reviews'),

    
]