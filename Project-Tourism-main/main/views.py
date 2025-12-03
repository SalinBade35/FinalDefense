
from django.shortcuts import render, redirect, get_object_or_404
from .models import Event
import json


from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re  # Import the regular expression module

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib import messages

from .models import *


# _____________________________________________________________________________________________________________

def index(request):
    # Get the latest 3 upcoming events
    latest_events = Event.objects.filter(
        status='upcoming',
        start_date__gte=timezone.now()
    ).order_by('start_date')[:3]
    
    context = {
        'latest_events': latest_events
    }
    return render(request, "main/index.html", context)

@login_required(login_url='log_in')
def community(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        visit_date = request.POST.get('visit_date')
        location = request.POST.get('location')
        image = request.FILES.get('images')

        experience = TravelExperience(
            title=title,
            content=content,
            visit_date=visit_date,
            location=location,
            images=image,
            author=request.user
        )
        experience.save()
        return redirect('community')
    
    context = {
    'experiences': TravelExperience.objects.all().order_by('-created_at'),
    }


    return render(request, 'main/community.html', context)


@login_required(login_url='log_in')
def contribution(request):
    sites = HeritageSite.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        site_id = request.POST.get('associated_site')
        media = request.FILES.get('media')
        source = request.POST.get('source')
        verified = request.POST.get('verified') == 'on'

        site = HeritageSite.objects.get(id=site_id) if site_id else None

        Contribution.objects.create(
            title=title,
            content=content,
            associated_site=site,
            media=media,
            source=source,
            verified=verified,
            contributor=request.user
        )
        return redirect('contribution')
    
    contributions = Contribution.objects.order_by('-created_at') 

    return render(request, 'main/contribution.html', {'sites': sites,  'contributions': contributions})

#___________________________authentication starts here____________________________________________________
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Check if passwords match
        if password == confirm_password:
            try:
                # Check if the email ends with @gmail.com
                if not email.endswith('@gmail.com'):
                    messages.error(request, 'Please enter a valid Gmail address!!!')
                    return redirect('register')

                # Check if username or email already exists
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username already exists!!!')
                    return redirect('register')
                
                elif User.objects.filter(email=email).exists():
                    messages.error(request, 'Email already exists!!!')
                    return redirect('register')

                # Password strength checks
                # if len(password) < 8:
                #     messages.error(request, 'Password must be at least 8 characters long!!!')
                #     return redirect('register')
                # elif not re.search(r'[A-Z]', password):
                #     messages.error(request, 'Password must contain at least one uppercase letter!!!')
                #     return redirect('register')
                # elif not re.search(r'[0-9]', password):
                #     messages.error(request, 'Password must contain at least one numeric digit!!!')
                #     return redirect('register')
                # elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                #     messages.error(request, 'Password must contain at least one special character!!!')
                #     return redirect('register')
                # elif username.lower() in password.lower():
                #     messages.error(request, 'Password must not contain the username!!!')

                # Validate password strength using Django's built-in validation
                validate_password(password)

                # Create the user
                User.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password
                )
                # Display a thank you message with the username
                messages.success(request, f'Thank you for registering, {username}!!!')
                return redirect('log_in')

            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
                return redirect('register')
        else:
            messages.error(request, 'Passwords do not match!!!')
            return redirect('register')

    return render(request, 'sam/register.html')
    # return render(request, 'sam/register.html')

#  by specifying return redirect('page_name'), we're also specify where the message will appear.

def log_in(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        remember_me = request.POST.get('remember_me') # T or F

        if not User.objects.filter(username=username):
            messages.error(request,"Username does not exist")
            return redirect('log_in')
        else:
            user=authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                if remember_me:
                    request.session.set_expiry(592200) # for 7 days 
                else:
                    request.session.set_expiry(0)
                messages.success(request,"login successful")
                return redirect('index')
            else:
                messages.error(request,"Incorrect Password")
                return redirect('log_in')
    return render(request,'sam/login.html')

def log_out(request):
    logout(request)
    return redirect('log_in')
    


@login_required(login_url='log_in')
def change_password(request):
    form=PasswordChangeForm(user=request.user)
    if request.method=='POST':
        form=PasswordChangeForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('log_in')      
    
    return render(request,'sam/change_password.html',{'form':form})

@login_required
def user_profile(request):
    return render(request, 'sam/user_profile.html')

#___________________________authentication ends here____________________________________________________



# _________________________________food__________________________________________________________________

def ingredient_shop(request,id):
    data=Ingredient.objects.get(id=id)
    dd=Shop.objects.filter(ingredients=data)
    d = OnlineShop.objects.filter(ingredient=data)
    return render(request,'food/ingredient_shop.html',{'data':data,'shops':dd,'online_shops':d})

def recipe(request,id):
    food=Food.objects.get(id=id)
    data=Recipe.objects.get(name=food)
    return render(request,'food/recipe.html',{'recipe':data})

def historical_significance(request,id):
    food=Food.objects.get(id=id)
    data=Historical_Significance.objects.get(name=food)
    return render(request,'food/historical_significance.html',{'data':data})

def listoffood(request):
    data=Food.objects.all()
    return render(request,'food/listoffood.html',{'data':data})

def tutorial(request,id):
    food=Food.objects.get(id=id)
    return render(request,'food/video_tutorial.html',{'food':food})

def online_buying(request,id):
    food=Food.objects.get(id=id)
    data=OnlineBuying.objects.filter(name=food)
    return render(request,'food/online_buying.html',{'data':data,'food':food})

def restaurant(request,id):
    food=Food.objects.get(id=id)
    data=Restaurant.objects.filter(food=food)
    return render(request,'food/restaurant.html',{'data':data})



# _____________________________________________tourism services________________________________________________

def tourism_services(request):
    transportation=Transportation.objects.all()
    accomodation=Accomodation.objects.all()
    tourguides=TourGuides.objects.all()
    return render(request,'tourism_services/tourism_services.html',{'transportation':transportation,'accomodation':accomodation,'tourguides':tourguides})




# _____________________________________________Weather__________________________________________________________




from .utils import get_weather_data  # use .utils if you rename the file

import requests
from collections import defaultdict
from django.shortcuts import render

def weather_view(request):
    API_KEY = 'c9085be2ba255f1ff15d56c7dfb6c9a9'
    city = request.GET.get('city', '').strip()
    country = request.GET.get('country', '').strip().upper()

    weather = None
    forecast = []

    if city:
        # Build query for OpenWeatherMap
        query = city
        if country:
            query += f",{country}"

        # Fetch current weather
        current_url = f'https://api.openweathermap.org/data/2.5/weather?q={query}&appid={API_KEY}&units=metric'
        current_response = requests.get(current_url)
        current_data = current_response.json()

        if current_data.get('cod') == 200:
            weather = {
                'city': current_data['name'],
                'temperature': round(current_data['main']['temp'], 1),
                'description': current_data['weather'][0]['description'],
                'humidity': current_data['main']['humidity'],
                'wind': current_data['wind']['speed'],
                'icon_url': f"http://openweathermap.org/img/wn/{current_data['weather'][0]['icon']}@2x.png"
            }

        # Fetch 5-day forecast
        forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={query}&appid={API_KEY}&units=metric'
        forecast_response = requests.get(forecast_url)
        forecast_data = forecast_response.json()

        if forecast_data.get('cod') == '200':
            daily_data = defaultdict(list)
            for entry in forecast_data.get('list', []):
                date = entry['dt_txt'].split(' ')[0]
                daily_data[date].append(entry)

            for date, entries in list(daily_data.items())[:5]:
                temps = [e['main']['temp'] for e in entries]
                descriptions = [e['weather'][0]['description'] for e in entries]
                humidities = [e['main']['humidity'] for e in entries]
                winds = [e['wind']['speed'] for e in entries]
                icons = [e['weather'][0]['icon'] for e in entries]
                forecast.append({
                    'date': date,
                    'avg_temp': round(sum(temps) / len(temps), 1),
                    'description': descriptions[0],
                    'humidity': round(sum(humidities) / len(humidities)),
                    'wind': round(sum(winds) / len(winds), 1),
                    'icon_url': f"http://openweathermap.org/img/wn/{icons[0]}@2x.png"
                })

    return render(request, 'main/weather.html', {
        'weather': weather,
        'forecast': forecast,
        'city': city,
        'country': country
    })


from django.http import JsonResponse

def weather_api(request):
    location = request.GET.get('location', '').strip()
    if not location:
        return JsonResponse({'success': False, 'error': 'No location provided'})

    api_key = 'c9085be2ba255f1ff15d56c7dfb6c9a9'
    url = f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric'

    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get('cod') != 200:
            return JsonResponse({'success': False, 'error': 'Weather not found'})
        weather = {
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'condition': data['weather'][0]['main'],
            'humidity': data['main']['humidity'],
            'windSpeed': round(data['wind']['speed'] * 3.6, 2),  # m/s to km/h
        }
        return JsonResponse({'success': True, 'weather': weather})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# _____________________________________________Weather ends__________________________________________________________



# ------------------------------------sampada's code starts here-------------------------
# ------------------------------------sampada's code starts here-------------------------

# _____________________________________________Event__________________________________________________________





def events_view(request):
    events = Event.objects.all()
    events_json = json.dumps([
    {
        'id': event.id,
        'title': event.title,
        'category': event.event_type,
        'date': event.start_date.isoformat(),
        'end_date': event.end_date.isoformat() if event.end_date else None,  # <-- Add this line

        'time': event.start_date.strftime('%H:%M') if event.start_date else '', 
        'location': event.location,
        'about': event.description,  # <-- make sure this is included!
    }
    for event in events
])
    return render(request, "event/events.html", {
        "events": events,
        "events_json": events_json,
    })




def events_page(request):
    events = Event.objects.all()
    return render(request, 'event/events.html', {'events': events})

def learnmore_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event/learnmore.html', {'event': event})

def get_event_directions(request, event_id):
    """Handle directions requests for events"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        start_address = request.POST.get('start_address', '').strip()
        travel_mode = request.POST.get('travel_mode', 'car')
        
        # Get destination coordinates (same logic as event_map)
        destination_coordinates = None
        start_coordinates = None
        map_style_url = None
        error_message = None
        
        # Get destination coordinates from event
        if event.location:
            try:
                client = get_baato_client()
                search_response = client.search(q=event.location)
                
                if search_response and search_response.get("status") == 200:
                    data = search_response.get("data", [])
                    
                    if data:
                        first_result = data[0]
                        place_id = first_result.get("placeId")
                        
                        if place_id:
                            places_response = client.places(place_id=place_id)
                            
                            if places_response and places_response.get("status") == 200:
                                place_data = places_response.get("data")
                                
                                if place_data and len(place_data) > 0:
                                    first_place = place_data[0]
                                    
                                    if "centroid" in first_place:
                                        lat = first_place["centroid"]["lat"]
                                        lon = first_place["centroid"]["lon"]
                                        destination_coordinates = {"lat": lat, "lon": lon}
                                        
                                        # Generate map style URL
                                        map_style_url = f"https://api.baato.io/api/v1/styles/breeze?key={settings.BAATO_API_KEY}"
                
            except Exception as e:
                print(f"Error getting destination coordinates: {e}")
                logger.error(f"Error getting destination coordinates for {event.name}: {e}")
        
        # Get start coordinates from start address
        if start_address and destination_coordinates:
            try:
                client = get_baato_client()
                start_search_response = client.search(q=start_address)
                
                if start_search_response and start_search_response.get("status") == 200:
                    start_data = start_search_response.get("data", [])
                    
                    if start_data:
                        start_result = start_data[0]
                        start_place_id = start_result.get("placeId")
                        
                        if start_place_id:
                            start_places_response = client.places(place_id=start_place_id)
                            
                            if start_places_response and start_places_response.get("status") == 200:
                                start_place_data = start_places_response.get("data")
                                
                                if start_place_data and len(start_place_data) > 0:
                                    start_first_place = start_place_data[0]
                                    
                                    if "centroid" in start_first_place:
                                        start_lat = start_first_place["centroid"]["lat"]
                                        start_lon = start_first_place["centroid"]["lon"]
                                        start_coordinates = {"lat": start_lat, "lon": start_lon}
                
            except Exception as e:
                print(f"Error getting start coordinates: {e}")
                logger.error(f"Error getting start coordinates for {start_address}: {e}")
                error_message = "Could not find the starting location. Please check the address and try again."
        
        # Get directions if both coordinates are available
        directions_data = None
        if start_coordinates and destination_coordinates and not error_message:
            try:
                # Make direct API call to Baato directions API
                url = f"https://api.baato.io/api/v1/directions"
                params = {
                    'key': settings.BAATO_API_KEY,
                    'points[]': [
                        f"{start_coordinates['lat']},{start_coordinates['lon']}",
                        f"{destination_coordinates['lat']},{destination_coordinates['lon']}"
                    ],
                    'mode': travel_mode
                }
                
                response = requests.get(url, params=params)
                directions_response = response.json()
                
                if directions_response.get("status") == 200 and directions_response.get("data"):
                    directions_data = directions_response["data"][0]
                else:
                    error_message = "No route found between the specified locations."
                    
            except Exception as e:
                print(f"Error getting directions: {e}")
                logger.error(f"Error getting directions: {e}")
                error_message = "Unable to get directions at this time. Please try again later."
        
        elif not start_coordinates and not error_message:
            error_message = "Could not find the starting location. Please check the address and try again."
        elif not destination_coordinates:
            error_message = "Destination location is not available for this event."
        
        # Prepare context data
        context = {
            'event': event,
            'start_address': start_address,
            'travel_mode': travel_mode,
            'error_message': error_message,
            'has_location': bool(destination_coordinates),
            'map_style_url': map_style_url,
            'start_coordinates': start_coordinates,
            'destination_coordinates': destination_coordinates,
        }
        
        # Add directions data if available
        if directions_data and not error_message:
            # Handle the API response format
            distance_m = directions_data.get('distanceInMeters', 0)
            duration_ms = directions_data.get('timeInMs', 0)
            
            distance_km = round(distance_m / 1000, 1)
            duration_minutes = round(duration_ms / (1000 * 60))  # Convert milliseconds to minutes
            
            # Get travel mode display info
            travel_mode_info = {
                'car': {'display': 'Driving', 'icon': 'car'},
                'bike': {'display': 'Cycling', 'icon': 'bicycle'},
                'foot': {'display': 'Walking', 'icon': 'walking'}
            }
            
            mode_info = travel_mode_info.get(travel_mode, {'display': 'Driving', 'icon': 'car'})
            
            # Handle instructions - they might be None
            instructions = directions_data.get('instructionList', [])
            if instructions is None:
                instructions = []
            
            context.update({
                'distance_km': distance_km,
                'duration_minutes': duration_minutes,
                'travel_mode_display': mode_info['display'],
                'travel_mode_icon': mode_info['icon'],
                'directions': instructions,
                'encoded_polyline': directions_data.get('encodedPolyline', ''),  # For future use if needed
            })
        
        return render(request, 'event/directions_result.html', context)
    
    # If not POST, redirect back to event map
    return redirect('event_map', event_id=event_id)

def event_map(request, event_id):
    """Display map for an event"""
    event = get_object_or_404(Event, id=event_id)
    
    # Get coordinates from address if available
    coordinates = None
    map_style_url = None
    
    if event.location:
        try:
            client = get_baato_client()
            search_response = client.search(q=event.location)
            
            if search_response and search_response.get("status") == 200:
                data = search_response.get("data", [])
                
                if data:
                    first_result = data[0]
                    place_id = first_result.get("placeId")
                    
                    if place_id:
                        # Use the places method to get place details with coordinates
                        places_response = client.places(place_id=place_id)
                        
                        if places_response and places_response.get("status") == 200:
                            place_data = places_response.get("data")
                            
                            # place_data is an array, get the first item
                            if place_data and len(place_data) > 0:
                                first_place = place_data[0]
                                
                                if "centroid" in first_place:
                                    lat = first_place["centroid"]["lat"]
                                    lon = first_place["centroid"]["lon"]
                                    coordinates = {"lat": lat, "lon": lon}
                                    print(f"Coordinates found from places API: {coordinates}")
                                    
                                    # Generate Baato map style URL with API key
                                    map_style_url = f"https://api.baato.io/api/v1/styles/breeze?key={settings.BAATO_API_KEY}"
                                
        except Exception as e:
            print(f"Exception occurred: {e}")
            logger.error(f"Error getting coordinates for {event.name}: {e}")
    else:
        print("No location available for this event")
    
    context = {
        'event': event,
        'coordinates': coordinates,
        'map_style_url': map_style_url,
        'has_location': bool(coordinates),
        'BAATO_API_KEY': settings.BAATO_API_KEY,
    }
    
    return render(request, 'event/event_map.html', context)
# _____________________________________________Event ends__________________________________________________________

# _____________________________________________Wishlist starts__________________________________________________________

def wishlist(request, site_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('log_in')  # Redirect to login if user is not authenticated
        
        site = get_object_or_404(Sites, id=site_id)
        
        # Check if the site is already in the user's wishlist
        existing_entry = Wishlist.objects.filter(user=request.user, site=site).first()
        if existing_entry:
            existing_entry.delete()
            Wishlist.objects.create(user=request.user, site=site)
        else:
            # Add to wishlist
            Wishlist.objects.create(user=request.user, site=site)
        
        return redirect('site_detail', id=site_id)  # Redirect back to site detail page
    
    return redirect('site_detail', id=site_id)  # Redirect back if not POST

@login_required
def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('site')
    return render(request, 'wishlist/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def remove_from_wishlist(request, site_id):
    """Remove specific item from wishlist"""
    site = get_object_or_404(Sites, id=site_id)
    
    wishlist_item = Wishlist.objects.filter(user=request.user, site=site).first()
    wishlist_item.delete()
    return redirect('view_wishlist')


# _____________________________________________sites__________________________________________________________

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Sites
from baato import BaatoClient
from django.conf import settings
import logging
logger = logging.getLogger(__name__)
def get_baato_client():
    """Initialize Baato client"""
    return BaatoClient(
        access_token=settings.BAATO_API_KEY,
        endpoint="https://api.baato.io/api",
        version="v1"
    )

def listofsites(request):
    sites = Sites.objects.all()
    return render(request, 'sites/listofsites.html', {'sites': sites})

def site_detail(request, id):
    site = Sites.objects.get(id=id)
    
    # Get coordinates from address if available
    coordinates = None
    map_style_url = None

    
    if site.map_address:
        try:
            client = get_baato_client()
            search_response = client.search(q=site.map_address)
            
            print(f"Search response: {search_response}")
            
            if search_response and search_response.get("status") == 200:
                data = search_response.get("data", [])
                
                if data:
                    first_result = data[0]
                    place_id = first_result.get("placeId")
                    print(f"Found placeId: {place_id}")
                    
                    if place_id:
                        # Use the places method to get place details with coordinates
                        places_response = client.places(place_id=place_id)
                        print(f"Places response: {places_response}")
                        
                        if places_response and places_response.get("status") == 200:
                            place_data = places_response.get("data")
                            
                            # place_data is an array, get the first item
                            if place_data and len(place_data) > 0:
                                first_place = place_data[0]
                                
                                if "centroid" in first_place:
                                    lat = first_place["centroid"]["lat"]
                                    lon = first_place["centroid"]["lon"]
                                    coordinates = {"lat": lat, "lon": lon}
                                    print(f"Coordinates found from places API: {coordinates}")
                                    
                                    # Generate Baato map style URL with API key
                                    map_style_url = f"https://api.baato.io/api/v1/styles/breeze?key={settings.BAATO_API_KEY}"
                                
        except Exception as e:
            print(f"Exception occurred: {e}")
            logger.error(f"Error getting coordinates for {site.name}: {e}")
    else:
        print("No map_address available for this site")
    
    context = {
        'site': site,
        'data': {
            'description': site.description,
            'history': site.history,
            'cultural_significance': site.cultural_significance
        },
        'coordinates': coordinates,
        'map_style_url': map_style_url,
        'has_location': bool(coordinates),
        'BAATO_API_KEY': settings.BAATO_API_KEY,
    }
    
    return render(request, 'sites/site_detail.html', context)


def get_directions(request, id):
    site = Sites.objects.get(id=id)
    
    if request.method == 'POST':
        start_address = request.POST.get('start_address', '').strip()
        travel_mode = request.POST.get('travel_mode', 'car')
        
        # Get destination coordinates (same logic as site_detail)
        destination_coordinates = None
        start_coordinates = None
        map_style_url = None
        error_message = None
        
        # Get destination coordinates from site
        if site.map_address:
            try:
                client = get_baato_client()
                search_response = client.search(q=site.map_address)
                
                if search_response and search_response.get("status") == 200:
                    data = search_response.get("data", [])
                    
                    if data:
                        first_result = data[0]
                        place_id = first_result.get("placeId")
                        
                        if place_id:
                            places_response = client.places(place_id=place_id)
                            
                            if places_response and places_response.get("status") == 200:
                                place_data = places_response.get("data")
                                
                                if place_data and len(place_data) > 0:
                                    first_place = place_data[0]
                                    
                                    if "centroid" in first_place:
                                        lat = first_place["centroid"]["lat"]
                                        lon = first_place["centroid"]["lon"]
                                        destination_coordinates = {"lat": lat, "lon": lon}
                                        
                                        # Generate map style URL
                                        map_style_url = f"https://api.baato.io/api/v1/styles/breeze?key={settings.BAATO_API_KEY}"
                
            except Exception as e:
                print(f"Error getting destination coordinates: {e}")
                logger.error(f"Error getting destination coordinates for {site.name}: {e}")
        
        # Get start coordinates from start address
        if start_address and destination_coordinates:
            try:
                client = get_baato_client()
                start_search_response = client.search(q=start_address)
                
                if start_search_response and start_search_response.get("status") == 200:
                    start_data = start_search_response.get("data", [])
                    
                    if start_data:
                        start_result = start_data[0]
                        start_place_id = start_result.get("placeId")
                        
                        if start_place_id:
                            start_places_response = client.places(place_id=start_place_id)
                            
                            if start_places_response and start_places_response.get("status") == 200:
                                start_place_data = start_places_response.get("data")
                                
                                if start_place_data and len(start_place_data) > 0:
                                    start_first_place = start_place_data[0]
                                    
                                    if "centroid" in start_first_place:
                                        start_lat = start_first_place["centroid"]["lat"]
                                        start_lon = start_first_place["centroid"]["lon"]
                                        start_coordinates = {"lat": start_lat, "lon": start_lon}
                
            except Exception as e:
                print(f"Error getting start coordinates: {e}")
                logger.error(f"Error getting start coordinates for {start_address}: {e}")
                error_message = "Could not find the starting location. Please check the address and try again."
        
        # Get directions if both coordinates are available
        directions_data = None
        if start_coordinates and destination_coordinates and not error_message:
            try:
                import requests
                
                # Make direct API call to Baato directions API
                url = f"https://api.baato.io/api/v1/directions"
                params = {
                    'key': settings.BAATO_API_KEY,
                    'points[]': [
                        f"{start_coordinates['lat']},{start_coordinates['lon']}",
                        f"{destination_coordinates['lat']},{destination_coordinates['lon']}"
                    ],
                    'mode': travel_mode
                }
                
                response = requests.get(url, params=params)
                directions_response = response.json()
                
                
                if directions_response.get("status") == 200 and directions_response.get("data"):
                    directions_data = directions_response["data"][0]
                else:
                    error_message = "No route found between the specified locations."
                    
            except Exception as e:
                print(f"Error getting directions: {e}")
                logger.error(f"Error getting directions: {e}")
                error_message = "Unable to get directions at this time. Please try again later."
        
        elif not start_coordinates and not error_message:
            error_message = "Could not find the starting location. Please check the address and try again."
        elif not destination_coordinates:
            error_message = "Destination location is not available for this site."
        
        # Prepare context data
        context = {
            'site': site,
            'start_address': start_address,
            'travel_mode': travel_mode,
            'error_message': error_message,
            'has_location': bool(destination_coordinates),
            'map_style_url': map_style_url,
            'start_coordinates': start_coordinates,
            'destination_coordinates': destination_coordinates,
        }
        
        # Add directions data if available
        if directions_data and not error_message:
            # Handle the API response format - note the field names
            distance_m = directions_data.get('distanceInMeters', 0)
            duration_ms = directions_data.get('timeInMs', 0)
            
            distance_km = round(distance_m / 1000, 1)
            duration_minutes = round(duration_ms / (1000 * 60))  # Convert milliseconds to minutes
            
            # Get travel mode display info
            travel_mode_info = {
                'car': {'display': 'Driving', 'icon': 'car'},
                'bike': {'display': 'Cycling', 'icon': 'bicycle'},
                'foot': {'display': 'Walking', 'icon': 'walking'}
            }
            
            mode_info = travel_mode_info.get(travel_mode, {'display': 'Driving', 'icon': 'car'})
            
            # Handle instructions - they might be None
            instructions = directions_data.get('instructionList', [])
            if instructions is None:
                instructions = []
            
            context.update({
                'distance_km': distance_km,
                'duration_minutes': duration_minutes,
                'travel_mode_display': mode_info['display'],
                'travel_mode_icon': mode_info['icon'],
                'directions': instructions,
                'encoded_polyline': directions_data.get('encodedPolyline', ''),  # For future use if needed
            })
        
        return render(request, 'sites/directions_result.html', context)
    
    # If not POST, redirect back to site detail
    return redirect('site_detail', id=id)


logger = logging.getLogger(__name__)

def get_baato_client():
    """Helper function to get Baato client"""
    return BaatoClient(
        access_token=settings.BAATO_API_KEY,
        endpoint="https://api.baato.io/api",
        version="v1"
    )

def nearby_places(request, id, place_type):
    """
    Unified view for nearby sites, accommodations, and restaurants
    """
    site = get_object_or_404(Sites, id=id)
    
    # Get site coordinates first (reusing your existing logic)
    coordinates = None
    map_style_url = None
    places_data = []
    
    if site.map_address:
        try:
            client = get_baato_client()
            search_response = client.search(q=site.map_address)
            
            print(f"Search response: {search_response}")
            
            if search_response and search_response.get("status") == 200:
                data = search_response.get("data", [])
                
                if data:
                    first_result = data[0]
                    place_id = first_result.get("placeId")
                    print(f"Found placeId: {place_id}")
                    
                    if place_id:
                        # Get place details with coordinates
                        places_response = client.places(place_id=place_id)
                        print(f"Places response: {places_response}")
                        
                        if places_response and places_response.get("status") == 200:
                            place_data = places_response.get("data")
                            
                            if place_data and len(place_data) > 0:
                                first_place = place_data[0]
                                
                                if "centroid" in first_place:
                                    lat = first_place["centroid"]["lat"]
                                    lon = first_place["centroid"]["lon"]
                                    coordinates = {"lat": lat, "lon": lon}
                                    print(f"Coordinates found: {coordinates}")
                                    
                                    # Generate Baato map style URL
                                    map_style_url = f"https://api.baato.io/api/v1/styles/breeze?key={settings.BAATO_API_KEY}"
                                    
                                    # Now search for nearby places
                                    places_data = search_nearby_places(client, lat, lon, place_type)
                                    
        except Exception as e:
            print(f"Exception occurred: {e}")
            logger.error(f"Error getting coordinates for {site.name}: {e}")
    
    # Define display names and descriptions
    place_info = {
        'sites': {
            'title': 'Nearby Tourist Sites',
            'description': 'Tourist attractions, museums, and points of interest'
        },
        'accommodations': {
            'title': 'Nearby Accommodations', 
            'description': 'Hotels, guest houses, and lodging options'
        },
        'restaurants': {
            'title': 'Nearby Restaurants',
            'description': 'Restaurants, cafes, and dining options'
        },
        'transportations':{
            'title': 'Nearby Transportations',
            'description': 'Bus stations and bus stops'
        }
    }
    
    context = {
        'site': site,
        'places': places_data,
        'place_type': place_type,
        'place_info': place_info.get(place_type, {}),
        'coordinates': coordinates,
        'map_style_url': map_style_url,
        'has_location': bool(coordinates),
        'BAATO_API_KEY': settings.BAATO_API_KEY,
    }
    
    return render(request, 'sites/nearby_places.html', context)

def search_nearby_places(client, lat, lon, place_type):
    """
    Search for nearby places based on type using Baato API
    """
    places_data = []
    
    # Define search types for each category based on Baato API merged types
    search_types = {
        'sites': ['tourism', 'attraction', 'museum', 'park'],
        'accommodations': ['hotel', 'guest_house', 'resort', 'hostel'],
        'transportations' : ['bus_station', 'bus_stop'],
        'restaurants': ['eat', 'cafe', 'restaurant'],  # 'eat' is merged type in Baato
    }
    
    types_to_search = search_types.get(place_type, [])
    
    for search_type in types_to_search:
        try:
            print(f"Searching for type: {search_type}")
            
            # Use the near_by method as specified in the documentation
            response = client.near_by(
                lat=lat,
                lon=lon,
                type=search_type,
                limit=10,
                radius=5  # 5km radius
            )
            
            print(f"Nearby response for {search_type}: {response}")
            
            if response and response.get("status") == 200:
                data = response.get("data", [])
                
                for place in data:
                    # Extract place information
                    place_info = {
                        'placeId': place.get('placeId'),
                        'name': place.get('name', 'Unknown Place'),
                        'address': place.get('address', 'Address not available'),
                        'type': place.get('type', search_type),
                        'lat': place.get('centroid', {}).get('lat', 0),
                        'lon': place.get('centroid', {}).get('lon', 0),
                        'distance': place.get('radialDistanceInKm', 'N/A'),
                        'open': place.get('open', None),
                        'tags': place.get('tags', [])
                    }
                    
                    # Extract additional info from tags
                    phone = None
                    opening_hours = None
                    email = None
                    
                    for tag in place_info['tags']:
                        if tag.startswith('phone|'):
                            phone = tag.split('|', 1)[1]
                        elif tag.startswith('opening_hours|'):
                            opening_hours = tag.split('|', 1)[1]
                        elif tag.startswith('email|'):
                            email = tag.split('|', 1)[1]
                    
                    place_info.update({
                        'phone': phone,
                        'opening_hours': opening_hours,
                        'email': email
                    })
                    
                    places_data.append(place_info)
                    
        except Exception as e:
            print(f"Error searching for {search_type}: {e}")
            logger.error(f"Error searching for {search_type}: {e}")
    
    # Sort by distance if available
    places_data.sort(key=lambda x: float(x['distance']) if x['distance'] != 'N/A' else float('inf'))
    
    return places_data

# Individual view functions for URL routing
def nearby_sites(request, id):
    return nearby_places(request, id, 'sites')

def nearby_accommodations(request, id):
    return nearby_places(request, id, 'accommodations')

def nearby_restaurants(request, id):
    return nearby_places(request, id, 'restaurants')

def nearby_transportations(request, id):
    return nearby_places(request, id, 'transportations')


# _____________________________________________Wishlist ends__________________________________________________________
# sampada's code ends here