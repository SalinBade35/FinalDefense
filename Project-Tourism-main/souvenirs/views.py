import re
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count, Avg  # Add Avg here
from .models import Category, Product, CartItem, Order, OrderItem, WishlistItem, Review,Payment
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
import uuid
import hmac
import hashlib
import base64
import requests
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
import json


def category_list_view(request):
    categories = Category.objects.annotate(product_count=Count('products'))
    all_products_count = Product.objects.count()
    return render(request, 'categories.html', {
        'categories': categories,
        'all_products_count': all_products_count
    })

def product_list_view(request):
    queryset = Product.objects.prefetch_related('categories')
    categories = Category.objects.all()

    search = request.GET.get('search', '')
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    category = request.GET.get('category', '')
    if category and category != 'all':
        queryset = queryset.filter(categories__slug=category)

    price = request.GET.get('price', 'all')
    if price == 'low':
        queryset = queryset.filter(price__lt=20)
    elif price == 'mid':
        queryset = queryset.filter(price__gte=20, price__lte=50)
    elif price == 'high':
        queryset = queryset.filter(price__gt=50)

    wishlist_count = 0
    cart_count = 0
    if request.user.is_authenticated:
        wishlist_count = WishlistItem.objects.filter(user=request.user).count()
        cart_count = CartItem.objects.filter(user=request.user).count()

    context = {
        'products': queryset.distinct(),
        'categories': categories,
        'search': search,
        'selected_category': category,
        'selected_price': price,
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
    }
    return render(request, 'souvenirs/souvenirs.html', context)





@login_required
@require_POST
def submit_review(request, product_id):
    from django.utils.html import escape
    product = get_object_or_404(Product, id=product_id)
    rating = int(request.POST.get('rating', 0))
    comment = request.POST.get('comment', '').strip()
    if not (1 <= rating <= 5):
        return JsonResponse({'success': False, 'error': 'Invalid rating.'}, status=400)
    # Prevent duplicate reviews
    review, created = Review.objects.update_or_create(
        product=product, user=request.user,
        defaults={'rating': rating, 'comment': escape(comment)}
    )
    # Update product's average rating and review count
    product_avg = product.reviews.aggregate(avg=Avg('rating'), count=Count('id'))  # Fixed: use Avg
    avg_rating = product_avg['avg'] or 0
    review_count = product_avg['count']
    return JsonResponse({
        'success': True,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'review': {
            'user': request.user.username,
            'rating': rating,
            'comment': comment,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M')
        }
    })

def get_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.select_related('user').order_by('-created_at')
    data = [{
        'user': r.user.username,
        'rating': r.rating,
        'comment': r.comment,
        'created_at': r.created_at.strftime('%Y-%m-%d %H:%M')
    } for r in reviews]
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0  # Fixed: use Avg
    review_count = reviews.count()
    return JsonResponse({
        'reviews': data,
        'avg_rating': avg_rating,
        'review_count': review_count
    })




def ajax_product_search(request):
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    price = request.GET.get('price', 'all')
    
    queryset = Product.objects.prefetch_related('categories')
    
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    if category and category != 'all':
        queryset = queryset.filter(categories__slug=category)
    
    if price == 'low':
        queryset = queryset.filter(price__lt=20)
    elif price == 'mid':
        queryset = queryset.filter(price__gte=20, price__lte=50)
    elif price == 'high':
        queryset = queryset.filter(price__gt=50)
    
    products = queryset.distinct()
    html = render_to_string('souvenirs/_product_grid.html', {'products': products}, request=request)
    
    return JsonResponse({'html': html})

def static_product_detail_view(request):
    """Static product details view for demo purposes"""
    static_product_data = {
        'product': {
            'id': 1,
            'name': 'RadhaKrishna Painting',
            'description': 'Beautiful handmade oil painting of Lord Shree Krishna holding flute with Radha. This exquisite artwork captures the divine love and spiritual essence of the eternal couple. Perfect for home decoration or as a spiritual gift.',
            'price': 100.00,
            'rating': 4.5,
            'reviews': 5,
            'in_stock': 42,
            'image': None,
            'image_url': 'https://via.placeholder.com/500x500?text=RadhaKrishna+Painting',
        },
        'is_in_stock': True,
    }
    return render(request, 'souvenirs/product_detail.html', static_product_data)

def product_detail_view(request, product_id):
    """Dynamic product details view"""
    product = get_object_or_404(Product, id=product_id)
    is_in_stock = product.in_stock > 0
    
    context = {
        'product': product,
        'is_in_stock': is_in_stock,
    }
    return render(request, 'souvenirs/product_detail.html', context)

@login_required
@require_POST
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id)
    
    if product.in_stock <= 0:
        return JsonResponse({'success': False, 'error': 'Product is out of stock'})
    
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity >= product.in_stock:
            return JsonResponse({'success': False, 'error': 'Not enough stock available'})
        cart_item.quantity += 1
        cart_item.save()
    
    cart_count = CartItem.objects.filter(user=request.user).count()
    return JsonResponse({'success': True, 'cart_count': cart_count})

@login_required
def get_cart_items(request):
    """Get user's cart items"""
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    
    items = []
    for item in cart_items:
        items.append({
            'id': item.id,
            'name': item.product.name,
            'price': str(item.product.price),
            'quantity': item.quantity,
            'image': item.product.image.url if item.product.image else item.product.image_url,
        })
    
    return JsonResponse({'items': items})

@login_required
@require_POST
def remove_cart_item(request):
    """Remove item from cart"""
    item_id = request.POST.get('item_id')
    try:
        cart_item = CartItem.objects.get(id=item_id, user=request.user)
        cart_item.delete()
        return JsonResponse({'success': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})

@login_required
@require_POST
def update_cart_quantity(request):
    """Update cart item quantity"""
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        cart_item = CartItem.objects.get(id=item_id, user=request.user)
        
        if quantity <= 0:
            cart_item.delete()
        elif quantity <= cart_item.product.in_stock:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            return JsonResponse({'success': False, 'error': 'Not enough stock'})
        
        return JsonResponse({'success': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})

@login_required
@require_POST
def add_to_wishlist(request):
    """Add product to wishlist"""
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    
    wishlist_item, created = WishlistItem.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    wishlist_count = WishlistItem.objects.filter(user=request.user).count()
    return JsonResponse({'success': True, 'wishlist_count': wishlist_count})

@login_required
def get_wishlist_items(request):
    """Get user's wishlist items"""
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('product')
    
    items = []
    for item in wishlist_items:
        items.append({
            'id': item.product.id,
            'name': item.product.name,
            'price': str(item.product.price),
            'image': item.product.image.url if item.product.image else item.product.image_url,
        })
    
    return JsonResponse({'items': items})

@login_required
@require_POST
def remove_wishlist_item(request):
    """Remove item from wishlist"""
    product_id = request.POST.get('product_id')
    try:
        wishlist_item = WishlistItem.objects.get(product_id=product_id, user=request.user)
        wishlist_item.delete()
        return JsonResponse({'success': True})
    except WishlistItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})

@login_required
@require_POST
def wishlist_add_to_cart(request):
    """Add wishlist item to cart"""
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    
    if product.in_stock <= 0:
        return JsonResponse({'success': False, 'error': 'Product is out of stock'})
    
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity >= product.in_stock:
            return JsonResponse({'success': False, 'error': 'Not enough stock available'})
        cart_item.quantity += 1
        cart_item.save()
    
    return JsonResponse({'success': True})


@login_required
def delivery_view(request):
    """
    Display delivery form.
    If ?product=ID&qty=QTY is present, treat as direct buy for that product only.
    Otherwise, use cart items.
    """
    product_id = request.GET.get('product')
    qty = request.GET.get('qty')
    cart_items = None
    direct_buy = False
    single_product = None
    total_amount = 0

    if product_id and qty:
        try:
            product = Product.objects.get(id=product_id)
            quantity = int(qty)
            if quantity < 1 or quantity > product.in_stock:
                quantity = 1
            # Create a dummy object to mimic cart item
            class DummyItem:
                def __init__(self, product, quantity):
                    self.product = product
                    self.quantity = quantity
                    self.total_price = product.price * quantity
            cart_items = [DummyItem(product, quantity)]
            direct_buy = True
            single_product = product
            total_amount = product.price * quantity
        except (Product.DoesNotExist, ValueError):
            cart_items = []
    else:
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        direct_buy = False
        total_amount = sum(item.product.price * item.quantity for item in cart_items)

    if not cart_items or (not direct_buy and not cart_items.exists()):
        return redirect('souvenirs:souvenir_list')

    context = {
        'cart_items': cart_items,
        'direct_buy': direct_buy,
        'single_product': single_product,
        'total_amount': total_amount,
    }
    return render(request, 'souvenirs/delivery.html', context)

@login_required
@require_POST
def process_delivery_order(request):
    """Process the order from delivery page"""
    # Check if it's a direct buy
    direct_buy = request.POST.get('direct_buy') == '1'
    product_id = request.POST.get('direct_buy_product')
    qty = request.POST.get('direct_buy_qty')

    if direct_buy and product_id and qty:
        # Handle direct buy
        try:
            product = Product.objects.get(id=product_id)
            quantity = int(qty)
            if quantity > product.in_stock:
                return JsonResponse({
                    'success': False, 
                    'error': f'Insufficient stock for {product.name}. Only {product.in_stock} available.'
                }, status=400)
            # Create a temporary cart item list for processing
            class DummyItem:
                def __init__(self, product, quantity):
                    self.product = product
                    self.quantity = quantity
                    self.total_price = product.price * quantity
            cart_items = [DummyItem(product, quantity)]
        except (Product.DoesNotExist, ValueError):
            return JsonResponse({'success': False, 'error': 'Invalid product or quantity.'}, status=400)
    else:
        # Handle regular cart
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return JsonResponse({'success': False, 'error': 'Cart is empty.'}, status=400)

    # Get form data
    first_name = request.POST.get('firstName', '').strip()
    last_name = request.POST.get('lastName', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    address = request.POST.get('address', '').strip()
    city = request.POST.get('city', '').strip()
    state = request.POST.get('state', '').strip()
    zip_code = request.POST.get('zip', '').strip()
    special_instructions = request.POST.get('specialInstructions', '').strip()
    call_before = request.POST.get('callBefore') == 'on'
    leave_at_door = request.POST.get('leaveAtDoor') == 'on'

    # Validation (unchanged)
    if not all([first_name, last_name, email, phone, address, city, state, zip_code]):
        return JsonResponse({'success': False, 'error': 'All required fields must be filled.'}, status=400)
    if city.lower() != 'bhaktapur':
        return JsonResponse({'success': False, 'error': 'We only deliver within Bhaktapur city.'}, status=400)
    if state != 'Bagmati':
        return JsonResponse({'success': False, 'error': 'Invalid province selected. Please select Bagmati Province.'}, status=400)
    ward_pattern = r'^44800-0[1-9]|44800-10$'
    if not re.match(ward_pattern, zip_code):
        return JsonResponse({'success': False, 'error': 'Please select a valid ward number for Bhaktapur.'}, status=400)
    if len(address) < 1:
        return JsonResponse({'success': False, 'error': 'Please provide a detailed address including ward, tole/street, and landmarks.'}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'success': False, 'error': 'Please enter a valid email address.'}, status=400)
    mobile_pattern = r'^98[0-9]{8}$'
    landline_pattern = r'^01-[0-9]{7}$'
    if not (re.match(mobile_pattern, phone) or re.match(landline_pattern, phone)):
        return JsonResponse({'success': False, 'error': 'Please enter a valid Nepal phone number (Mobile: 98XXXXXXXX or Landline: 01-XXXXXXX)'}, status=400)
    full_phone_number = f"+977{phone}"
    ward_number = zip_code.split('-')[1]
    full_address = f"{address}\nWard {ward_number}, {city}, {state} Province, Nepal\nPostal Code: 44800"
    if special_instructions:
        full_address += f"\n\nSpecial Instructions: {special_instructions}"
    if call_before:
        full_address += "\n• Call before delivery"
    if leave_at_door:
        full_address += "\n• Leave at door if not available"

    total_amount = sum(item.total_price for item in cart_items)
    order = Order.objects.create(
        session_key=request.user.username,
        total_amount=total_amount,
        address=full_address,
        customer_name=f"{first_name} {last_name}",
        customer_email=email,
        customer_phone=full_phone_number
    )

    # Create order items and update stock
    for cart_item in cart_items:
        if cart_item.quantity > cart_item.product.in_stock:
            return JsonResponse({
                'success': False, 
                'error': f'Insufficient stock for {cart_item.product.name}. Only {cart_item.product.in_stock} available.'
            }, status=400)
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        cart_item.product.in_stock -= cart_item.quantity
        cart_item.product.save()

    # Clear cart only if it's not direct buy
    if not (direct_buy and product_id and qty):
        CartItem.objects.filter(user=request.user).delete()

    return redirect('souvenirs:initiate_payment', order_id=order.id)


def genSha256(key, message):
    key = key.encode('utf-8')
    message = message.encode('utf-8')

    hmac_sha256 = hmac.new(key, message, hashlib.sha256)
    digest = hmac_sha256.digest()

    # Convert the digest to a Base64-encoded string
    signature = base64.b64encode(digest).decode('utf-8')

    return signature
def initiate_payment(request, order_id):
    # Example data
    order=get_object_or_404(Order,id=order_id)
    amount = order.total_amount
    tax_amount = 0
    total_amount = amount + tax_amount
    transaction_uuid = str(uuid.uuid4())  # Generate unique UUID
    product_code = "EPAYTEST"
    success_url = f"http://127.0.0.1:8000/souvenirs/paymentsuccess/{order_id}/?q={order_id}"
    failure_url = "http://127.0.0.1:8000/souvenirs/payment/failed/"

    # Create the hash signature
    secret_key = "8gBm/:&EnhH.1/q"
    data_to_sign = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code=EPAYTEST"

    signature = genSha256(secret_key, data_to_sign)

    context = {
        'amount': amount,
        'tax_amount': tax_amount,
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code': product_code,
        'success_url': success_url,
        'failure_url': failure_url,
        'signature': signature,
    }
    return render(request, 'payment/payment_ways.html', context)


def verify_payment(request):
    transaction_id = request.GET.get('q')  # Transaction ID from eSewa
    ref_id = request.GET.get('refId')  # Reference ID from eSewa

    url = "https://uat.esewa.com.np/epay/transrec"
    data = {
        'amt': "total_amount",  # Amount to verify
        'rid': ref_id,  # Reference ID
        'pid': transaction_id,  # Your transaction ID
        'scd': "merchant_code"  # Your merchant code
    }

    response = requests.post(url, data=data)
    if "Success" in response.text:
        return JsonResponse({"status": "Payment Verified"})
    return JsonResponse({"status": "Payment Verification Failed"})

def decode_base64(data):
    decoded_data = base64.b64decode(data).decode('utf-8')
    print(decoded_data)
    return json.loads(decoded_data)

def payment_failed(request):
    messages.error(request, "Payment failed. Please try again.")
    return redirect('rooms')

def paymentsuccess(request,order_id):
    order=get_object_or_404(Order,id=order_id)
    payment_method='e-Sewa'
    amount_paid=order.total_amount
    payment_completed=False
    Payment.objects.create(Order=order,payment_method=payment_method,amount_paid=amount_paid,payment_completed=payment_completed)
    User=request.user
    subject="Thankyou for buying!!"
    message=render_to_string('payment/success.html',{'Order':order})
    from_email="salinbade1994@gmail.com"
    recipient_list=[User.email]
    msg_email=EmailMessage(subject,message,from_email,recipient_list)
    msg_email.send(fail_silently=True)
    return render(request,'payment/payment_success.html',{'Order':order})



#  ESewa Payment Integration Views

# @csrf_exempt
# def esewa_success(request):
#     # eSewa will POST transaction details here
#     # You should verify the transaction with eSewa's verification API
#     # If verified, create the order as paid
#     # For demo, just show a success message
#     return render(request, 'souvenirs/esewa_success.html')

# @csrf_exempt
# def esewa_failure(request):
#     return render(request, 'souvenirs/esewa_failure.html')