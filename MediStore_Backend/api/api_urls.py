from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    AdminUserViewSet, AdminStatsViewSet,
    LoginViewSet, RegisterViewSet, CategoryViewSet, ProductViewSet,
    CartViewSet, OrderViewSet, PrescriptionViewSet, AddressViewSet,
    UserProfileViewSet, ReviewViewSet, ApplyCouponViewSet
)

router = DefaultRouter()
router.register(r'admin/users', AdminUserViewSet, basename='admin_users')
router.register(r'admin/stats', AdminStatsViewSet, basename='admin_stats')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    # REST API
    path('', include(router.urls)),
    
    # Authentication
    path('auth/login/', LoginViewSet.as_view({'post': 'post'}), name='api_login'),
    path('auth/register/', RegisterViewSet.as_view({'post': 'post'}), name='api_register'),
    
    # Cart
    path('cart/', CartViewSet.as_view({
        'get': 'get'
    }), name='api_cart'),
    path('cart/add_item/', CartViewSet.as_view({
        'post': 'add_item'
    }), name='api_cart_add_item'),
    path('cart/update_item/', CartViewSet.as_view({
        'post': 'update_item'
    }), name='api_cart_update_item'),
    path('cart/remove_item/', CartViewSet.as_view({
        'post': 'remove_item'
    }), name='api_cart_remove_item'),
    path('cart/clear/', CartViewSet.as_view({
        'post': 'clear'
    }), name='api_cart_clear'),

    path('apply_coupon/', ApplyCouponViewSet.as_view({'post': 'post'}), name='apply_coupon'),
    
    # User Profile
    path('profile/', UserProfileViewSet.as_view({
        'get': 'get',
        'put': 'update',
        'patch': 'update'
    }), name='api_profile'),
    
]
