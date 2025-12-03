from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from .models import Category, Product, CartItem, Order, OrderItem, WishlistItem, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'created_date']
    list_filter = ['name']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    def product_count(self, obj):
        count = obj.products.count()
        if count > 0:
            url = reverse('admin:souvenirs_product_changelist') + f'?categories__id__exact={obj.id}'
            return format_html('<a href="{}">{} products</a>', url, count)
        return '0 products'
    product_count.short_description = 'Products'
    product_count.admin_order_field = 'product_count'
    
    def created_date(self, obj):
        return "Available"
    created_date.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count=Count('products')
        )

class DiscountFilter(admin.SimpleListFilter):
    title = 'discount status'
    parameter_name = 'discount'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'With Discount'),
            ('no', 'Regular Price'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(original_price__isnull=False, original_price__gt=F('price'))
        if self.value() == 'no':
            return queryset.filter(Q(original_price__isnull=True) | Q(original_price__lte=F('price')))

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'image_preview', 'get_categories', 'pricing_display', 
        'stock_status', 'bestseller', 'created_at'
    ]
    list_filter = [
        'categories', 'bestseller', 'created_at', DiscountFilter
    ]
    search_fields = ['name', 'description', 'categories__name']
    list_editable = ['bestseller']
    readonly_fields = ['created_at', 'updated_at', 'discount_info', 'image_preview']
    filter_horizontal = ['categories']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'categories'),
            'classes': ('wide',)
        }),
        ('Media', {
            'fields': ('image', 'image_preview', 'image_url', 'purchase_url'),
            'classes': ('collapse',)
        }),
        ('Pricing & Inventory', {
            'fields': (
                ('price', 'original_price'),
                'discount_info',
                ('in_stock', 'bestseller')
            ),
            'classes': ('wide',),
            'description': 'Set "price" as the selling price. Add "original_price" only if there\'s a discount.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def pricing_display(self, obj):
        if obj.has_discount:
            return format_html(
                '<div style="line-height: 1.2;">'
                '<strong style="color: #e74c3c; font-size: 14px;">${}</strong><br>'
                '<span style="color: #95a5a6; text-decoration: line-through; font-size: 12px;">${}</span> '
                '<span style="background: #e74c3c; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px; font-weight: bold;">{}% OFF</span>'
                '</div>',
                obj.price, obj.original_price, obj.discount_percentage
            )
        else:
            return format_html(
                '<strong style="color: #27ae60; font-size: 14px;">${}</strong>',
                obj.price
            )
    pricing_display.short_description = 'Pricing'
    pricing_display.admin_order_field = 'price'
    
    def discount_info(self, obj):
        if obj.has_discount:
            return format_html(
                '<div style="padding: 10px; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #e74c3c;">'
                '<strong style="color: #e74c3c;">Discount Active</strong><br>'
                'Discount: <strong>{}%</strong><br>'
                'Savings: <strong>${}</strong><br>'
                'Original Price: <strong>${}</strong><br>'
                'Sale Price: <strong>${}</strong>'
                '</div>',
                obj.discount_percentage, obj.savings_amount, obj.original_price, obj.price
            )
        else:
            return format_html(
                '<div style="padding: 10px; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #27ae60;">'
                '<strong style="color: #27ae60;">Regular Pricing</strong><br>'
                'No discount applied<br>'
                'Price: <strong>${}</strong>'
                '</div>',
                obj.price
            )
    discount_info.short_description = 'Pricing Details'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;"/>',
                obj.image.url
            )
        elif obj.image_url:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;"/>',
                obj.image_url
            )
        return "No image"
    image_preview.short_description = 'Preview'
    
    def get_categories(self, obj):
        categories = obj.categories.all()
        if categories:
            category_links = []
            for category in categories:
                url = reverse('admin:souvenirs_category_change', args=[category.id])
                category_links.append(f'<a href="{url}">{category.name}</a>')
            return mark_safe(', '.join(category_links))
        return "No categories"
    get_categories.short_description = 'Categories'
    
    def stock_status(self, obj):
        if obj.in_stock == 0:
            return format_html(
                '<span style="color: #e74c3c; font-weight: bold;">Out of Stock</span>'
            )
        elif obj.in_stock <= 5:
            return format_html(
                '<span style="color: #f39c12; font-weight: bold;">{} (Low Stock)</span>',
                obj.in_stock
            )
        else:
            return format_html(
                '<span style="color: #27ae60; font-weight: bold;">{} Available</span>',
                obj.in_stock
            )
    stock_status.short_description = 'Stock'
    stock_status.admin_order_field = 'in_stock'
    
    actions = ['mark_as_bestseller', 'remove_bestseller', 'mark_out_of_stock']
    
    def mark_as_bestseller(self, request, queryset):
        updated = queryset.update(bestseller=True)
        self.message_user(request, f'{updated} products marked as bestsellers.')
    mark_as_bestseller.short_description = "Mark selected products as bestsellers"
    
    def remove_bestseller(self, request, queryset):
        updated = queryset.update(bestseller=False)
        self.message_user(request, f'{updated} products removed from bestsellers.')
    remove_bestseller.short_description = "Remove bestseller status"
    
    def mark_out_of_stock(self, request, queryset):
        updated = queryset.update(in_stock=0)
        self.message_user(request, f'{updated} products marked as out of stock.')
    mark_out_of_stock.short_description = "Mark as out of stock"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'comment_preview', 'created_at']
    list_filter = ['rating', 'created_at', 'product__categories']
    search_fields = ['product__name', 'user__username', 'comment']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def comment_preview(self, obj):
        if obj.comment:
            return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
        return 'No comment'
    comment_preview.short_description = 'Comment'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        'cart_owner', 'product_link', 'quantity', 'unit_price', 
        'total_price_display', 'created_at'
    ]
    list_filter = ['created_at', 'product__categories']
    search_fields = ['user__username', 'session_key', 'product__name']
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def cart_owner(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return f'Guest ({obj.session_key[:8]}...)'
    cart_owner.short_description = 'Customer'
    
    def product_link(self, obj):
        url = reverse('admin:souvenirs_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    
    def unit_price(self, obj):
        return f'${obj.product.price}'
    unit_price.short_description = 'Unit Price'
    
    def total_price_display(self, obj):
        return format_html(
            '<strong style="color: #27ae60;">${}</strong>',
            obj.total_price
        )
    total_price_display.short_description = 'Total'
    total_price_display.admin_order_field = 'total_price'

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['user_link', 'product_link', 'added_at']
    list_filter = ['added_at', 'product__categories']
    search_fields = ['user__username', 'product__name']
    date_hierarchy = 'added_at'
    ordering = ['-added_at']
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'Customer'
    
    def product_link(self, obj):
        url = reverse('admin:souvenirs_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['product', 'quantity', 'price', 'total_price']
    
    def total_price(self, obj):
        return f'${obj.quantity * obj.price}'
    total_price.short_description = 'Total'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id', 'customer_info', 'total_amount_display',
        'items_count', 'order_date'
    ]

    search_fields = [
        'id', 'session_key', 'customer_name', 'customer_email', 
        'customer_phone', 'address'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'items_summary', 'formatted_address'
    ]
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('Order Information', {
            'fields': ('session_key', 'payment_method'),
            'classes': ('wide',)
        }),
        ('Customer Information', {
            'fields': (
                ('customer_name', 'customer_email'),
                'customer_phone',
                'formatted_address'
            ),
            'classes': ('wide',)
        }),
        ('Financial Information', {
            'fields': ('total_amount', 'items_summary'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def order_id(self, obj):
        return f'#{obj.id}'
    order_id.short_description = 'Order ID'
    order_id.admin_order_field = 'id'
    
    def customer_info(self, obj):
        if obj.customer_name and obj.customer_email:
            return format_html(
                '<strong>{}</strong><br>'
                '<small style="color: #7f8c8d;">{}</small><br>'
                '<small style="color: #7f8c8d;">{}</small>',
                obj.customer_name, obj.customer_email, obj.customer_phone or 'No phone'
            )
        return f'Guest ({obj.session_key[:8]}...)'
    customer_info.short_description = 'Customer'
    
    
    
    def total_amount_display(self, obj):
        return format_html(
            '<strong style="color: #27ae60; font-size: 14px;">${}</strong>',
            obj.total_amount
        )
    total_amount_display.short_description = 'Total'
    total_amount_display.admin_order_field = 'total_amount'
    
    def items_count(self, obj):
        items = obj.items.select_related('product').all()
        if not items:
            return format_html('<span style="color: #95a5a6; font-style: italic;">📭 No items</span>')
        
        item_details = []
        total_qty = 0
        
        for item in items:
            item_html = f'''
            <div style="padding: 4px; margin: 2px 0; background-color: #f8f9fa; border-left: 3px solid #3498db; border-radius: 3px;">
                <span style="font-weight: bold; color: #e74c3c;">{item.quantity}</span>× 
                <span style="color: #2c3e50;">{item.product.name}</span> 
                <span style="color: #27ae60; font-weight: bold;">(${float(item.price):.2f})</span>
            </div>
            '''
            item_details.append(item_html)
            total_qty += item.quantity
        
        summary = f'''
        <div style="margin-top: 6px; padding: 4px; background-color: #3498db; color: white; text-align: center; border-radius: 4px; font-weight: bold; font-size: 11px;">
            🛍️ {len(items)} items • {total_qty} pieces • ${float(obj.total_amount):.2f}
        </div>
        '''
        
        combined_html = f'''
        <div style="min-width: 200px; max-width: 300px;">
            {''.join(item_details)}
            {summary}
        </div>
        '''
        
        return format_html(combined_html)
    items_count.short_description = '🛒 Order Items'
    items_count.allow_tags = True
    
    def order_date(self, obj):
        return obj.created_at.strftime('%b %d, %Y at %I:%M %p')
    order_date.short_description = 'Order Date'
    order_date.admin_order_field = 'created_at'
    
    def items_summary(self, obj):
        items = obj.items.all()
        if items:
            summary = []
            for item in items:
                summary.append(f'• {item.quantity}x {item.product.name} (${item.price} each)')
            return format_html('<br>'.join(summary))
        return 'No items'
    items_summary.short_description = 'Order Items'
    
    def formatted_address(self, obj):
        if obj.address:
            return format_html(obj.address.replace('\n', '<br>'))
        return 'No address provided'
    formatted_address.short_description = 'Delivery Address'
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing', updated_at=timezone.now())
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_as_processing.short_description = "Mark as processing"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped', updated_at=timezone.now())
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = "Mark as shipped"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered', updated_at=timezone.now())
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_as_delivered.short_description = "Mark as delivered"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related().prefetch_related('items__product')

admin.site.site_header = "Tourism Souvenirs Administration"
admin.site.site_title = "Souvenirs Admin"
admin.site.index_title = "Welcome to Souvenirs Administration"