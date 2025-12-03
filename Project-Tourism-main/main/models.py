from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

class TravelExperience(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    visit_date = models.DateField()
    location = models.CharField(max_length=255)  # To be enhanced with map-based input (Leaflet.js)
    images = models.ImageField(upload_to='experience_images/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experiences')
    source = models.URLField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
 

    
class HeritageSite(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Contribution(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    associated_site = models.ForeignKey(HeritageSite, on_delete=models.SET_NULL, null=True)
    media = models.FileField(upload_to='contribution_media/', blank=True, null=True)
    source = models.URLField(blank=True, null=True)
    contributor = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    verified = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.title
    
class Ingredient(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
class Food(models.Model):
    name = models.CharField(max_length=100)
    short_description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    tutorial_video_url = models.URLField(blank=True, null=True)  # YouTube or external video URL

    def __str__(self):
        return self.name

class Historical_Significance(models.Model):
    name=models.OneToOneField(Food, on_delete=models.CASCADE, primary_key=True)
    history=models.TextField(blank=True, null=True)
    cultural_significance=models.TextField(blank=True, null=True)

class OnlineBuying(models.Model):
    name = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='buying_links')
    product_url = models.URLField(blank=True, null=True)


    
class Recipe(models.Model):
    name = models.OneToOneField(Food, on_delete=models.CASCADE, primary_key=True)
    description = models.TextField(blank=True, null=True)
    prep_time = models.IntegerField(blank=True, null=True)
    servings = models.IntegerField(blank=True, null=True)
    ingredient_list = models.ManyToManyField(Ingredient, related_name="recipes") 
    instructions = models.TextField(blank=True, null=True)
    carbohydrate = models.TextField(blank=True, null=True)  
    protein = models.TextField(blank=True, null=True)  
    fat = models.TextField(blank=True, null=True)  
    calories = models.TextField(blank=True, null=True)  
    image=models.ImageField(upload_to='img', blank=True, null=True)
   


class Shop(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)  
    maps_link = models.URLField(blank=True, null=True)  
    contact = models.CharField(max_length=20, blank=True, null=True)
    ingredients = models.ManyToManyField(Ingredient, related_name="shops")
    promocode=models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        
        return self.name
class OnlineShop(models.Model):
    name = models.CharField(max_length=100)  
    product_url = models.URLField(blank=True, null=True)  
    ingredient = models.ForeignKey(Ingredient, related_name="online_shops", on_delete=models.CASCADE)  

    def __str__(self):
        return f"{self.name} - {self.ingredient.name}"



class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)  
    maps_link = models.URLField(blank=True, null=True)  
    contact = models.CharField(max_length=20, blank=True, null=True)
    food=models.ManyToManyField(Food, related_name="restaurants")

    def __str__(self):
        return self.name

class Sites(models.Model):
    name = models.CharField(max_length=100)
    photo1=models.ImageField(upload_to='img', blank=True, null=True)
    photo2=models.ImageField(upload_to='img', blank=True, null=True)
    photo3=models.ImageField(upload_to='img', blank=True, null=True)
    shortdescription=models.TextField(blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    history=models.TextField(blank=True, null=True)
    cultural_significance=models.TextField(blank=True, null=True)
    
    map_address = models.CharField(max_length=255, blank=True, null=True, 
                                   help_text="Enter the address for map location")

    def __str__(self):
        return self.name
    
class Transportation(models.Model):
    name = models.CharField(max_length=100)
    photo=models.ImageField(upload_to='img', blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    phone=PhoneNumberField(region='NP',null=True,blank=True)
    link=models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Accomodation(models.Model):
    name = models.CharField(max_length=100)
    photo=models.ImageField(upload_to='img', blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    phone=PhoneNumberField(region='NP',null=True,blank=True)
    link=models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class TourGuides(models.Model):
    name = models.CharField(max_length=100)
    photo=models.ImageField(upload_to='img', blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    phone=PhoneNumberField(region='NP',null=True,blank=True)
    link=models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    


#_______________________________Events started at here#

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)  # For category icon CSS class or image path

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    EVENT_TYPE_CHOICES = [
        ('festival', 'Festival'),
        ('workshop', 'Workshop'),
        ('exhibition', 'Exhibition'),
        ('religious', 'Religious'),
        ('cultural', 'Cultural'),
        ('seasonal', 'Seasonal'),
        ('music', 'Music'),
        ('art', 'Art'),
        ('food', 'Food'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, related_name='events')
    tags = models.ManyToManyField(Tag, blank=True, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organizer = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-start_date']

class EventGallery(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='events/gallery/')
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Gallery image for {self.event.title}"
    
    

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    site = models.ForeignKey(Sites, on_delete=models.CASCADE)  
    def __str__(self):
        return f"{self.user.username} - {self.site.name}"