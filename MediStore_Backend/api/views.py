from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Prescription, Address
from .forms import (
    AddressForm, 
    PrescriptionUploadForm, CheckoutForm, UserRegistrationForm, 
    UserLoginForm, UserProfileForm
)


# ============ PUBLIC VIEWS ============

def index(request):
    """Home page with featured products"""
    featured_products = Product.objects.filter(discount_percentage__gt=0)[:8]
    categories = Category.objects.all()[:6]
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'index.html', context)


def product_listing(request):
    """Product catalog with search and filtering"""
    products = Product.objects.all()
    categories = Category.objects.all()
    search_query = request.GET.get('search', '')
    selected_category = request.GET.get('category', '')
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(brand__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if selected_category:
        products = products.filter(category__name=selected_category)
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': selected_category,
    }
    return render(request, 'products.html', context)


def product_detail(request, product_id):
    """Product detail page"""
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'product-detail.html', context)


# ============ AUTHENTICATION VIEWS ============

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create empty cart for new user
            Cart.objects.create(user=user)
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                if user.is_staff or user.is_superuser:
                    return redirect('admin_dashboard')
                return redirect('user_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# ============ CART VIEWS ============

@login_required(login_url='login')
def view_cart(request):
    """Cart page"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart.html', context)


@login_required(login_url='login')
@require_POST
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('view_cart')


@login_required(login_url='login')
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated!')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart!')
    
    return redirect('view_cart')


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from cart!')
    return redirect('view_cart')


# ============ CHECKOUT & ORDER VIEWS ============

@login_required(login_url='login')
def checkout(request):
    """Checkout page"""
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('view_cart')
    
    addresses = Address.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = CheckoutForm(request.user, request.POST)
        if form.is_valid():
            # Create order
            address = form.cleaned_data['address']
            payment_method = form.cleaned_data['payment_method']
            notes = form.cleaned_data.get('notes', '')
            
            subtotal = cart.total_price
            tax = subtotal * 0.05  # 5% tax
            shipping_charges = 50 if subtotal < 500 else 0
            total_amount = subtotal + tax + shipping_charges
            
            order = Order.objects.create(
                user=request.user,
                status='placed',
                payment_method=payment_method,
                address=address,
                subtotal=subtotal,
                tax=tax,
                shipping_charges=shipping_charges,
                total_amount=total_amount,
                notes=notes,
            )
            
            # Create order items from cart items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                    discount_percentage=cart_item.product.discount_percentage,
                )
            
            # Clear cart
            cart.items.all().delete()
            
            messages.success(request, f'Order placed successfully! Order ID: {order.order_number}')
            return redirect('order_detail', order_id=order.id)
    else:
        form = CheckoutForm(request.user)
    
    context = {
        'cart': cart,
        'form': form,
        'addresses': addresses,
    }
    return render(request, 'checkout.html', context)


@login_required(login_url='login')
def order_history(request):
    """User's order history"""
    orders = Order.objects.filter(user=request.user)
    
    context = {
        'orders': orders,
    }
    return render(request, 'order-history.html', context)


@login_required(login_url='login')
def order_detail(request, order_id):
    """Order detail and tracking"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'order-detail.html', context)


# ============ PRESCRIPTION VIEWS ============

@login_required(login_url='login')
def upload_prescription(request):
    """Upload prescription"""
    if request.method == 'POST':
        form = PrescriptionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.user = request.user
            prescription.save()
            messages.success(request, 'Prescription uploaded successfully and pending review.')
            return redirect('user_dashboard')
    else:
        form = PrescriptionUploadForm()
    
    return render(request, 'upload-prescription.html', {'form': form})


@login_required(login_url='login')
def prescription_list(request):
    """User's prescriptions"""
    prescriptions = Prescription.objects.filter(user=request.user)
    
    context = {
        'prescriptions': prescriptions,
    }
    return render(request, 'prescriptions.html', context)


# ============ USER DASHBOARD VIEWS ============

@login_required(login_url='login')
def user_dashboard(request):
    """User dashboard"""
    recent_orders = Order.objects.filter(user=request.user)[:5]
    prescriptions = Prescription.objects.filter(user=request.user)[:3]
    addresses = Address.objects.filter(user=request.user)
    cart = Cart.objects.filter(user=request.user).first()
    
    context = {
        'recent_orders': recent_orders,
        'prescriptions': prescriptions,
        'addresses': addresses,
        'cart': cart,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def user_profile(request):
    """User profile page"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'user-profile.html', context)


# ============ ADDRESS MANAGEMENT VIEWS ============

@login_required(login_url='login')
def manage_addresses(request):
    """Manage user addresses"""
    addresses = Address.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('manage_addresses')
    else:
        form = AddressForm()
    
    context = {
        'addresses': addresses,
        'form': form,
    }
    return render(request, 'manage-addresses.html', context)


@login_required(login_url='login')
def edit_address(request, address_id):
    """Edit address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('manage_addresses')
    else:
        form = AddressForm(instance=address)
    
    context = {
        'form': form,
        'address': address,
    }
    return render(request, 'edit-address.html', context)


@login_required(login_url='login')
def delete_address(request, address_id):
    """Delete address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully!')
    return redirect('manage_addresses')


# ============ ADMIN DASHBOARD VIEWS ============

@login_required(login_url='login')
def admin_dashboard(request):
    """Admin dashboard"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    pending_prescriptions = Prescription.objects.filter(status='pending').count()
    pending_orders = Order.objects.filter(status='placed').count()
    
    recent_orders = Order.objects.all()[:10]
    
    context = {
        'total_orders': total_orders,
        'total_users': total_users,
        'pending_prescriptions': pending_prescriptions,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
    }
    return render(request, 'admin.html', context)


def admin_test(request):
    """Admin diagnostic test page"""
    return render(request, 'admin-test.html')

