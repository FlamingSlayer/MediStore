from django.contrib import admin
from .models import Category, Product, Address, Prescription, Cart, CartItem, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'price', 'discount_price', 'prescription_required', 'stock']
    list_filter = ['category', 'prescription_required', 'created_at']
    search_fields = ['name', 'brand', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'brand', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_percentage')
        }),
        ('Details', {
            'fields': ('dosage', 'prescription_required', 'stock', 'image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'city', 'state', 'is_default']
    list_filter = ['city', 'state', 'is_default']
    search_fields = ['user__username', 'full_name', 'city']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'uploaded_at', 'expires_at']
    list_filter = ['status', 'uploaded_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['uploaded_at', 'reviewed_at']
    fieldsets = (
        ('User & File', {
            'fields': ('user', 'file')
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Expiry', {
            'fields': ('expires_at',)
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'reviewed_at'),
            'classes': ('collapse',)
        }),
    )


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['added_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_price', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'placed_at']
    list_filter = ['status', 'payment_method', 'placed_at']
    search_fields = ['order_number', 'user__username', 'user__email']
    readonly_fields = ['order_number', 'placed_at', 'confirmed_at', 'shipped_at', 'delivered_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Delivery', {
            'fields': ('address', 'prescription')
        }),
        ('Payment', {
            'fields': ('payment_method', 'subtotal', 'tax', 'shipping_charges', 'total_amount')
        }),
        ('Timeline', {
            'fields': ('placed_at', 'confirmed_at', 'shipped_at', 'delivered_at'),
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
