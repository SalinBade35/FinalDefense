# You need to install requests if you haven't: pip install requests

import requests
from datetime import datetime
from collections import defaultdict

API_KEY = 'c9085be2ba255f1ff15d56c7dfb6c9a9'
CITY = 'Bhaktapur'  # Change to your city
URL = f'https://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric'

response = requests.get(URL)
data = response.json()

# Group forecasts by date
daily_data = defaultdict(list)
for entry in data['list']:
    date = entry['dt_txt'].split(' ')[0]
    daily_data[date].append(entry)

# Summarize each day's weather (average temp, first description, etc.)
forecast = []
for date, entries in list(daily_data.items())[:5]:  # Next 5 days
    temps = [e['main']['temp'] for e in entries]
    descriptions = [e['weather'][0]['description'] for e in entries]
    humidities = [e['main']['humidity'] for e in entries]
    winds = [e['wind']['speed'] for e in entries]
    forecast.append({
        'date': date,
        'avg_temp': round(sum(temps) / len(temps), 1),
        'description': descriptions[0],
        'humidity': round(sum(humidities) / len(humidities)),
        'wind': round(sum(winds) / len(winds), 1),
    })

# Print the forecast
for day in forecast:
    print(f"{day['date']}: {day['avg_temp']}°C, {day['description']}, Humidity: {day['humidity']}%, Wind: {day['wind']} m/s")