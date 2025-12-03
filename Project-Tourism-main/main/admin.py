from django.contrib import admin
from .models import *

admin.site.register(HeritageSite)
admin.site.register(Contribution)
admin.site.register(TravelExperience)
admin.site.register(Recipe)
admin.site.register(Shop)
admin.site.register(OnlineShop)
admin.site.register(Restaurant)
admin.site.register(Ingredient)
admin.site.register(Food)
admin.site.register(Historical_Significance)
admin.site.register(OnlineBuying)
admin.site.register(Sites)
admin.site.register(Transportation)
admin.site.register(Accomodation)
admin.site.register(TourGuides)


#Events
admin.site.register(Category)
admin.site.register(Tag)

class EventGalleryInline(admin.TabularInline):
    model = EventGallery
    extra = 3  # Number of empty forms to display
    fields = ('image', 'caption')
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'location', 'status', 'is_featured')
    list_filter = ('status', 'event_type', 'is_featured', 'categories')
    search_fields = ('title', 'location', 'organizer')
    inlines = [EventGalleryInline]
    filter_horizontal = ('categories', 'tags')

@admin.register(EventGallery)
class EventGalleryAdmin(admin.ModelAdmin):
    list_display = ('event', 'caption', 'image')
    list_filter = ('event',)