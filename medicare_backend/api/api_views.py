from decimal import Decimal

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import F, Q, ExpressionWrapper, DecimalField, Sum, Count
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import (
    Address,
    Cart,
    CartItem,
    Category,
    Coupon,
    Order,
    OrderItem,
    Payment,
    Prescription,
    Product,
    Review,
)
from .serializers import (
    AddressSerializer,
    CartSerializer,
    CategorySerializer,
    OrderSerializer,
    PaymentSerializer,
    PrescriptionAdminUpdateSerializer,
    PrescriptionSerializer,
    ProductSerializer,
    ReviewSerializer,
    UserDetailSerializer,
    UserSerializer,
)

try:
    import razorpay  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    razorpay = None


class LoginViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if not user:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})


class RegisterViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        if not all([username, email, password]):
            return Response({'error': 'Username, email, and password required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        Cart.objects.create(user=user)
        token, _ = Token.objects.get_or_create(user=user)

        if user.email:
            send_mail(
                'Welcome to MediStore',
                f'Hi {user.first_name or user.username}, your MediStore account is ready.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )

        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        discount_factor = 1.0 - (F('discount_percentage') / 100.0)
        queryset = Product.objects.annotate(
            actual_price=ExpressionWrapper(F('price') * discount_factor, output_field=DecimalField())
        )

        category = self.request.query_params.get('category')
        if category:
            cats = [c.strip() for c in category.split(',')]
            query = Q()
            for cat in cats:
                query |= Q(category__name__icontains=cat)
            queryset = queryset.filter(query)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(brand__icontains=search) | Q(description__icontains=search)
            )

        prescription = self.request.query_params.get('prescription_required')
        if prescription:
            if prescription.lower() == 'true':
                queryset = queryset.filter(prescription_required=True)
            elif prescription.lower() == 'false':
                queryset = queryset.filter(prescription_required=False)

        max_price = self.request.query_params.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(actual_price__lte=float(max_price))
            except ValueError:
                pass

        ordering = self.request.query_params.get('ordering')
        if ordering:
            if ordering == 'discount_price':
                queryset = queryset.order_by('actual_price')
            elif ordering == '-discount_price':
                queryset = queryset.order_by('-actual_price')
            else:
                queryset = queryset.order_by(ordering)

        return queryset

    @action(detail=False, methods=['get'])
    def featured(self, request):
        products = Product.objects.filter(discount_percentage__gt=0)[:8]
        return Response(self.get_serializer(products, many=True).data)

    @action(detail=False, methods=['get'])
    def autocomplete(self, request):
        q = (request.query_params.get('q') or '').strip()
        if not q:
            return Response([])
        names = list(Product.objects.filter(name__icontains=q).values_list('name', flat=True).distinct()[:10])
        return Response(names)


class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({'error': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)

        if product.stock < quantity:
            return Response({'error': f'Insufficient stock for {product.name}'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
        if not created:
            if product.stock < (cart_item.quantity + quantity):
                return Response({'error': f'Insufficient stock for {product.name}'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def update_item(self, request):
        item_id = request.data.get('item_id') or request.data.get('cart_item_id')
        quantity = request.data.get('quantity')
        if not item_id or quantity is None:
            return Response({'error': 'item_id and quantity required'}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(quantity)
        if quantity > item.product.stock:
            return Response({'error': f'Only {item.product.stock} left for {item.product.name}'}, status=status.HTTP_400_BAD_REQUEST)

        if quantity > 0:
            item.quantity = quantity
            item.save()
            cart = item.cart
        else:
            cart = item.cart
            item.delete()

        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        item_id = request.data.get('item_id') or request.data.get('cart_item_id')
        if not item_id:
            return Response({'error': 'item_id required'}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart = item.cart
        item.delete()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()
        return Response(CartSerializer(cart).data)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().order_by('-placed_at')
        return Order.objects.filter(user=self.request.user).order_by('-placed_at')

    def create(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        address_id = request.data.get('address_id')
        payment_method = request.data.get('payment_method', 'cod')
        notes = request.data.get('notes', '')
        coupon_code = (request.data.get('coupon_code') or '').strip().upper()

        address = get_object_or_404(Address, id=address_id, user=request.user)

        for cart_item in cart.items.select_related('product'):
            if cart_item.product.stock < cart_item.quantity:
                return Response(
                    {'error': f'Insufficient stock for {cart_item.product.name}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        subtotal = cart.total_price
        coupon = None
        coupon_discount = Decimal('0.00')

        if coupon_code:
            coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
            if not coupon:
                return Response({'error': 'Invalid coupon code'}, status=status.HTTP_400_BAD_REQUEST)
            now = timezone.now()
            if not (coupon.valid_from <= now <= coupon.valid_to):
                return Response({'error': 'Coupon has expired or is not active yet'}, status=status.HTTP_400_BAD_REQUEST)
            if coupon.used_count >= coupon.max_uses:
                return Response({'error': 'Coupon usage limit reached'}, status=status.HTTP_400_BAD_REQUEST)

            if coupon.discount_type == 'percent':
                coupon_discount = (subtotal * coupon.discount_value) / Decimal('100')
            else:
                coupon_discount = coupon.discount_value
            coupon_discount = min(coupon_discount, subtotal)

        taxable_amount = subtotal - coupon_discount
        tax = taxable_amount * Decimal('0.05')
        shipping_charges = Decimal('50.00') if taxable_amount < Decimal('500.00') else Decimal('0.00')
        total_amount = taxable_amount + tax + shipping_charges

        order = Order.objects.create(
            user=request.user,
            status='placed',
            payment_method=payment_method,
            address=address,
            subtotal=subtotal,
            tax=tax,
            shipping_charges=shipping_charges,
            coupon_discount=coupon_discount,
            total_amount=total_amount,
            notes=notes,
            coupon=coupon,
        )

        for cart_item in cart.items.select_related('product'):
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                discount_percentage=cart_item.product.discount_percentage,
            )
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save(update_fields=['stock'])

        if coupon:
            coupon.used_count += 1
            coupon.save(update_fields=['used_count'])

        cart.items.all().delete()

        if request.user.email:
            send_mail(
                'Order Confirmation - MediStore',
                f'Your order {order.order_number} was created successfully.',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=True,
            )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def create_payment(self, request, pk=None):
        order = self.get_object()
        if order.user != request.user and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        if order.payment_method != 'online':
            return Response({'error': 'This order is not marked for online payment'}, status=status.HTTP_400_BAD_REQUEST)

        if order.payment_method == 'online' and razorpay is None:
            return Response({'error': 'Razorpay package not installed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
        key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
        if not key_id or not key_secret:
            return Response({'error': 'Razorpay keys are not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        client = razorpay.Client(auth=(key_id, key_secret))
        amount_paise = int(order.total_amount * Decimal('100'))
        rp_order = client.order.create(
            {
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': order.order_number,
                'payment_capture': 1,
            }
        )

        payment, _ = Payment.objects.update_or_create(
            order=order,
            defaults={
                'razorpay_order_id': rp_order['id'],
                'amount': order.total_amount,
                'status': 'created',
            },
        )

        payload = PaymentSerializer(payment).data
        payload['razorpay_key_id'] = key_id
        return Response(payload)

    @action(detail=True, methods=['post'])
    def payment_callback(self, request, pk=None):
        order = self.get_object()
        payment = get_object_or_404(Payment, order=order)

        razorpay_payment_id = request.data.get('razorpay_payment_id', '')
        razorpay_signature = request.data.get('razorpay_signature', '')
        razorpay_order_id = request.data.get('razorpay_order_id', '')

        if not all([razorpay_payment_id, razorpay_signature, razorpay_order_id]):
            payment.status = 'failed'
            payment.save(update_fields=['status'])
            return Response({'error': 'Missing callback data'}, status=status.HTTP_400_BAD_REQUEST)

        key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
        key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
        if razorpay is None or not key_id or not key_secret:
            payment.status = 'failed'
            payment.save(update_fields=['status'])
            return Response({'error': 'Payment gateway not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        client = razorpay.Client(auth=(key_id, key_secret))

        try:
            client.utility.verify_payment_signature(
                {
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature,
                }
            )
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'paid'
            payment.save(update_fields=['razorpay_payment_id', 'razorpay_signature', 'status'])
        except Exception:
            payment.status = 'failed'
            payment.save(update_fields=['status'])
            return Response({'error': 'Signature verification failed'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PaymentSerializer(payment).data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        status_new = request.data.get('status')

        if not status_new:
            return Response({'error': 'status is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_staff:
            can_cancel = status_new == 'cancelled' and order.status in ['placed', 'confirmed']
            if order.user != request.user or not can_cancel:
                return Response({'error': 'Permission denied or order cannot be cancelled'}, status=status.HTTP_403_FORBIDDEN)
        else:
            if status_new not in dict(Order.STATUS_CHOICES):
                return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = status_new
        if status_new == 'confirmed':
            order.confirmed_at = timezone.now()
        if status_new == 'shipped':
            order.shipped_at = timezone.now()
        if status_new == 'delivered':
            order.delivered_at = timezone.now()
        order.save()

        if order.user.email:
            send_mail(
                'Order Status Updated - MediStore',
                f'Order {order.order_number} is now {order.get_status_display()}.',
                settings.DEFAULT_FROM_EMAIL,
                [order.user.email],
                fail_silently=True,
            )

        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def request_return(self, request, pk=None):
        order = self.get_object()
        if order.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        if order.status != 'delivered':
            return Response({'error': 'Only delivered orders can be returned'}, status=status.HTTP_400_BAD_REQUEST)

        order.return_requested = True
        order.save(update_fields=['return_requested'])
        return Response({'message': 'Return request submitted', 'return_requested': True})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve_return(self, request, pk=None):
        order = self.get_object()
        if not order.return_requested:
            return Response({'error': 'No return request found'}, status=status.HTTP_400_BAD_REQUEST)

        order.return_requested = False
        order.status = 'cancelled'
        order.save(update_fields=['return_requested', 'status'])

        if order.user.email:
            send_mail(
                'Return Approved - MediStore',
                f'Your return request for order {order.order_number} has been approved.',
                settings.DEFAULT_FROM_EMAIL,
                [order.user.email],
                fail_silently=True,
            )

        return Response(OrderSerializer(order).data)


class PrescriptionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PrescriptionSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Prescription.objects.all()
        else:
            queryset = Prescription.objects.filter(user=self.request.user)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('-uploaded_at')

    def get_serializer_class(self):
        if self.action in ['partial_update', 'update'] and self.request.user.is_staff:
            return PrescriptionAdminUpdateSerializer
        return PrescriptionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        prescription = self.get_object()
        if not request.user.is_staff:
            return Response({'error': 'Only admin can review prescriptions'}, status=status.HTTP_403_FORBIDDEN)

        payload = request.data.copy()
        if 'notes' in payload and 'admin_notes' not in payload:
            payload['admin_notes'] = payload.get('notes')

        serializer = self.get_serializer(prescription, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        prescription.reviewed_at = timezone.now()
        prescription.save(update_fields=['reviewed_at'])

        if prescription.user.email:
            send_mail(
                'Prescription Status Update - MediStore',
                f'Your prescription has been {prescription.status}. Notes: {prescription.admin_notes or "N/A"}',
                settings.DEFAULT_FROM_EMAIL,
                [prescription.user.email],
                fail_silently=True,
            )

        return Response(PrescriptionSerializer(prescription).data)


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get(self, request):
        return Response(UserDetailSerializer(request.user).data)

    @action(detail=False, methods=['put', 'patch'])
    def update(self, request):
        user = request.user
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()
        return Response(UserDetailSerializer(user).data)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.select_related('user', 'product').all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        product_id = self.request.data.get('product')
        product = get_object_or_404(Product, id=product_id)

        has_purchased = OrderItem.objects.filter(
            order__user=self.request.user,
            order__status__in=['placed', 'confirmed', 'shipped', 'delivered'],
            product=product,
        ).exists()

        if not has_purchased:
            raise PermissionError('You can review only purchased products')

        serializer.save(user=self.request.user, product=product)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except PermissionError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class ApplyCouponViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def post(self, request):
        code = (request.data.get('code') or '').strip().upper()
        amount = Decimal(str(request.data.get('amount', '0')))
        coupon = Coupon.objects.filter(code=code, is_active=True).first()

        if not coupon:
            return Response({'error': 'Invalid coupon code'}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        if not (coupon.valid_from <= now <= coupon.valid_to):
            return Response({'error': 'Coupon is not valid now'}, status=status.HTTP_400_BAD_REQUEST)

        if coupon.used_count >= coupon.max_uses:
            return Response({'error': 'Coupon usage limit reached'}, status=status.HTTP_400_BAD_REQUEST)

        if coupon.discount_type == 'percent':
            discount = (amount * coupon.discount_value) / Decimal('100')
        else:
            discount = coupon.discount_value

        discount = min(discount, amount)
        final_total = amount - discount

        return Response(
            {
                'code': coupon.code,
                'discount': str(discount.quantize(Decimal('0.01'))),
                'discount_type': coupon.discount_type,
                'final_total': str(final_total.quantize(Decimal('0.01'))),
            }
        )


class AdminUserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request):
        users = User.objects.all().order_by('-date_joined')
        data = [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'is_staff': u.is_staff,
                'date_joined': u.date_joined,
            }
            for u in users
        ]
        return Response(data)


class AdminStatsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request):
        total_orders = Order.objects.count()
        total_users = User.objects.count()
        pending_prescriptions = Prescription.objects.filter(status='pending').count()
        pending_orders = Order.objects.filter(status='placed').count()
        revenue = Order.objects.filter(status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        return Response(
            {
                'total_orders': total_orders,
                'total_users': total_users,
                'pending_prescriptions': pending_prescriptions,
                'pending_orders': pending_orders,
                'revenue': revenue,
            }
        )

    @action(detail=False, methods=['get'])
    def chart(self, request):
        qs = (
            Order.objects.filter(status__in=['placed', 'confirmed', 'shipped', 'delivered'])
            .annotate(month=TruncMonth('placed_at'))
            .values('month')
            .annotate(order_count=Count('id'), revenue=Sum('total_amount'))
            .order_by('month')
        )

        data = [
            {
                'month': row['month'].strftime('%Y-%m') if row['month'] else '',
                'order_count': row['order_count'],
                'revenue': float(row['revenue'] or 0),
            }
            for row in qs
        ]
        return Response(data)
