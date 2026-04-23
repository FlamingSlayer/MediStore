from django.urls import path
from . import views

urlpatterns = [
    # ============ HOME & PRODUCTS ============
    path('', views.index, name='home'),
    path('products/', views.product_listing, name='product_listing'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # ============ AUTHENTICATION ============
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # ============ CART ============
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # ============ CHECKOUT & ORDERS ============
    path('checkout/', views.checkout, name='checkout'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # ============ PRESCRIPTIONS ============
    path('prescriptions/upload/', views.upload_prescription, name='upload_prescription'),
    
    # ============ USER DASHBOARD ============
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    
    # ============ ADMIN ============
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-test/', views.admin_test, name='admin_test'),
]
