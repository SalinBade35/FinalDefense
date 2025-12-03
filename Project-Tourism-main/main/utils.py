import requests

def get_weather_data():
    city = "Bhaktapur"
    api_key = "c9085be2ba255f1ff15d56c7dfb6c9a9"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("cod") == 200:
            wind_kmh = round(data["wind"]["speed"] * 3.6, 2)
            return {
                "city": city,
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"].title(),
                "humidity": data["main"]["humidity"],
                "wind": wind_kmh,
                "icon": data["weather"][0]["icon"],
                 "icon_url": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
            }
        else:
            return {"error": data.get("message", "Error retrieving data")}
    except Exception:
        return {"error": "Could not retrieve weather data."}