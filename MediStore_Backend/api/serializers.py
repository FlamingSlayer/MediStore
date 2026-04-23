import re
from html import escape
from urllib.parse import quote

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Prescription, Address, Payment, Review, Coupon, ShippingEvent


def _placeholder_style(name, category_name=''):
        haystack = f"{name or ''} {category_name or ''}".lower()
        styles = [
            ({'paracetamol', 'ibuprofen', 'pain', 'fever', 'diclo', 'dolo', 'calpol'}, {
                'bg_start': '#2a1a44', 'bg_end': '#14325f', 'accent_start': '#fb7185', 'accent_end': '#f97316', 'icon': 'tablet'
            }),
            ({'syrup', 'cough', 'cold', 'tonic', 'drops'}, {
                'bg_start': '#0f2748', 'bg_end': '#173a5a', 'accent_start': '#06b6d4', 'accent_end': '#0ea5a4', 'icon': 'bottle'
            }),
            ({'vitamin', 'multi', 'zinc', 'omega', 'calcium', 'b12', 'supplement'}, {
                'bg_start': '#2b2a11', 'bg_end': '#4a3c12', 'accent_start': '#f59e0b', 'accent_end': '#facc15', 'icon': 'capsule'
            }),
            ({'diabet', 'insulin', 'glu', 'sugar'}, {
                'bg_start': '#0f263f', 'bg_end': '#1a3b6d', 'accent_start': '#60a5fa', 'accent_end': '#22d3ee', 'icon': 'drop'
            }),
            ({'antibiotic', 'amox', 'azith', 'cef', 'clav'}, {
                'bg_start': '#1f2e3c', 'bg_end': '#233b50', 'accent_start': '#34d399', 'accent_end': '#14b8a6', 'icon': 'shield'
            }),
            ({'skin', 'cream', 'ointment', 'gel', 'lotion'}, {
                'bg_start': '#2d203f', 'bg_end': '#4b2c68', 'accent_start': '#a78bfa', 'accent_end': '#22d3ee', 'icon': 'tube'
            }),
        ]

        for keywords, style in styles:
            if any(keyword in haystack for keyword in keywords):
                return style

        return {
            'bg_start': '#1f2f57', 'bg_end': '#14213f',
            'accent_start': '#22d3ee', 'accent_end': '#60a5fa',
            'icon': 'plus'
        }


def _placeholder_icon(icon_type):
        icons = {
            'tablet': '<rect x="190" y="248" width="220" height="104" rx="34" fill="url(#accent)"/><line x1="300" y1="248" x2="300" y2="352" stroke="#ffffff" stroke-opacity="0.7" stroke-width="8"/>',
            'bottle': '<rect x="238" y="192" width="124" height="42" rx="12" fill="#d9f7ff" fill-opacity="0.85"/><rect x="210" y="228" width="180" height="206" rx="34" fill="url(#accent)"/><rect x="262" y="286" width="76" height="110" rx="16" fill="#ffffff" fill-opacity="0.35"/>',
            'capsule': '<rect x="178" y="252" width="244" height="96" rx="48" fill="url(#accent)"/><rect x="292" y="252" width="130" height="96" rx="48" fill="#ffffff" fill-opacity="0.22"/>',
            'drop': '<path d="M300 188 C355 266 380 307 380 352 C380 401 344 436 300 436 C256 436 220 401 220 352 C220 307 245 266 300 188 Z" fill="url(#accent)"/>',
            'shield': '<path d="M300 184 L390 224 V302 C390 363 354 414 300 438 C246 414 210 363 210 302 V224 Z" fill="url(#accent)"/><path d="M300 244 V362 M240 303 H360" stroke="#ffffff" stroke-width="14" stroke-linecap="round" stroke-opacity="0.75"/>',
            'tube': '<rect x="232" y="202" width="136" height="226" rx="28" fill="url(#accent)"/><rect x="250" y="170" width="100" height="44" rx="12" fill="#d9f7ff" fill-opacity="0.84"/><rect x="260" y="274" width="80" height="96" rx="14" fill="#ffffff" fill-opacity="0.35"/>',
            'plus': '<rect x="192" y="250" width="216" height="100" rx="30" fill="url(#accent)"/><rect x="282" y="180" width="36" height="240" rx="14" fill="#8bf5ff" fill-opacity="0.9"/>',
        }
        return icons.get(icon_type, icons['plus'])


def build_product_placeholder(name, category_name=''):
        style = _placeholder_style(name, category_name)
        raw_label = re.sub(r'\s+\d{8,}$', '', (name or 'Medicine')).strip()
        label = escape(raw_label[:20] or 'Medicine')
        icon_svg = _placeholder_icon(style['icon'])

        svg = f'''
<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
    <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="{style['bg_start']}"/>
            <stop offset="100%" stop-color="{style['bg_end']}"/>
        </linearGradient>
        <linearGradient id="accent" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="{style['accent_start']}"/>
            <stop offset="100%" stop-color="{style['accent_end']}"/>
        </linearGradient>
    </defs>
    <rect width="600" height="600" fill="url(#bg)"/>
    <circle cx="300" cy="295" r="150" fill="#ffffff" fill-opacity="0.06"/>
    {icon_svg}
    <text x="300" y="510" font-size="36" text-anchor="middle" fill="#e8f1ff" font-family="Segoe UI, Arial, sans-serif">{label}</text>
</svg>
'''.strip()
        return f"data:image/svg+xml;utf8,{quote(svg)}"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'name', 'brand', 'description',
            'dosage', 'price', 'discount_percentage', 'discount_price',
            'prescription_required', 'stock', 'image', 'created_at'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Remove accidental timestamp-like suffixes in names (e.g. "Smoke Product 2026034543").
        if data.get('name'):
            data['name'] = re.sub(r'\s+\d{8,}$', '', data['name']).strip()

        if not data.get('image'):
            data['image'] = build_product_placeholder(data.get('name'), data.get('category_name'))
        return data

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'full_name', 'phone', 'address_line_1', 'address_line_2',
            'city', 'state', 'postal_code', 'is_default'
        ]


class PrescriptionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'user_id', 'user_name', 'file', 'status', 'status_display', 'notes', 'admin_notes',
            'uploaded_at', 'reviewed_at', 'expires_at'
        ]


class PrescriptionAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['status', 'admin_notes']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'subtotal', 'added_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_items', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'quantity', 'price', 'discount_percentage',
            'subtotal', 'discount_amount', 'final_price'
        ]


class ShippingEventSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.username', read_only=True)

    class Meta:
        model = ShippingEvent
        fields = ['id', 'event_type', 'note', 'actor_name', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    shipping_events = ShippingEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display', 'payment_method',
            'payment_method_display', 'address', 'items', 'subtotal', 'tax',
            'shipping_charges', 'coupon_discount', 'coupon_code', 'total_amount',
            'return_requested', 'notes', 'courier_name', 'tracking_id',
            'shipping_notes', 'delivery_attempts', 'last_delivery_attempt_at',
            'shipping_events', 'placed_at',
            'confirmed_at', 'shipped_at', 'delivered_at'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['address', 'payment_method', 'notes']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'razorpay_order_id', 'razorpay_payment_id',
            'razorpay_signature', 'amount', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'product_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'discount_type', 'discount_value', 'valid_from',
            'valid_to', 'max_uses', 'used_count', 'is_active'
        ]
