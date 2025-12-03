from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    purchase_url = models.URLField(blank=True, null=True, help_text="External link to purchase this product")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Current selling price")
    original_price = models.DecimalField(
        max_digits=10, decimal_places=2, 
        blank=True, null=True,
        help_text="Original price (leave blank if no discount)"
    )
    categories = models.ManyToManyField(Category, related_name='products')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    bestseller = models.BooleanField(default=False)
    in_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def has_discount(self):
        """Check if product has a discount"""
        return self.original_price is not None and self.original_price > self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.has_discount:
            return round(((self.original_price - self.price) / self.original_price) * 100)
        return 0
    
    @property
    def display_price(self):
        """Get the main price to display"""
        return self.price
    
    @property
    def savings_amount(self):
        """Calculate savings amount"""
        if self.has_discount:
            return self.original_price - self.price
        return 0


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating}★ by {self.user.username} on {self.product.name}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)  # Make this nullable
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Change the unique constraint to handle both cases
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'], 
                condition=models.Q(user__isnull=False),
                name='unique_cart_item_user'
            ),
            models.UniqueConstraint(
                fields=['session_key', 'product'], 
                condition=models.Q(session_key__isnull=False),
                name='unique_cart_item_session'
            )
        ]
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        return self.quantity * self.product.price
    
    @property
    def total_savings(self):
        return self.quantity * (self.product.original_price - self.product.price)



class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.product.name} wishlisted by {self.user.username}"


class Order(models.Model):
    session_key = models.CharField(max_length=40)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.TextField(blank=True, null=True)
    
    # Separate contact info storage
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - ${self.total_amount}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Store price at time of order
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} - Order #{self.order.id}"
    
    @property
    def total_price(self):
        return self.quantity * self.price
    
class Payment(models.Model):
    Order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=[ ('e-Sewa', 'e-Sewa'), ('cash', 'Cash')])
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment for Order {self.Order.id} - {self.amount_paid}"