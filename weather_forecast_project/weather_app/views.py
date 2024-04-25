import os
import datetime
import json
import requests

from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .location import get_location_from_ip_address, get_lat_and_lon_from_city

# Get configuration settings 
load_dotenv()
API_KEY = os.getenv('WEATHER_API_KEY')
        

# Default variables for latitude and Longitude gotten from browser
LAT, LON = None, None

def index(request):

    # API URLs
    current_weather_url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}"
    forecast_weather_url = "https://api.openweathermap.org/data/3.0/onecall?lat={}&lon={}&exclude=current,minutely,hourly&appid={}"
    
    try:
        if request.method == "POST":
            city1 = request.POST['city1']

            # Get weather data and forcast for next 7 days for a city
            weather_data1, daily_forecasts1 = fetch_weather_and_forecast(city1, current_weather_url, forecast_weather_url, request)

            context = {
                'weather_data1': weather_data1,
                'daily_forecasts1': daily_forecasts1
            }
        else:
            weather_data2, daily_forecasts2 = fetch_weather_and_forecast(None, current_weather_url, forecast_weather_url, request)

            context = {
                'weather_data2': weather_data2,
                'daily_forecasts2': daily_forecasts2
            }
        return render(request, "weather_app/base.html", context) 
    except:
        messages.error(request, "An error occured.")

        return render(request, "weather_app/base.html")
   
def locate(request):
    """ Handle location data coming from Javascript frontend """

    if request.method == "POST":
        x = json.loads(request.body)
        global LAT, LON
        LAT = x['latitude']
        LON = x['longitude']
        print(f"{LAT} || {LON}")
        
        return JsonResponse({'message':'success'})
    else:
        return render(request, "weather_app/base.html")


def fetch_weather_and_forecast(city, current_weather_url, forecast_weather_url, request):
    """ This function returns a dictionary of daily weather and a list of dictionaries of weather forcast """

    if city == None:
        if LAT == None or LON == None: 
            # Get latitude and longitude for user form IP address location
            lat, lon = get_location_from_ip_address(request)
            print("1st")
            
        else:
            # Get latitude and longitude gotten from browser
            lat, lon = LAT, LON
            print('second') 
            print(f"{lat} || {lon}")
    else:
        # Get  latitude and longitude for city entered
        lat, lon = get_lat_and_lon_from_city(city, API_KEY)

    print(get_location_from_ip_address(request))
    print(current_weather_url.format(lat, lon, API_KEY))

    # Get weather data JSON from API and parse as dictionary
    response = requests.get(current_weather_url.format(lat, lon, API_KEY)).json()
    forecast_response = requests.get(forecast_weather_url.format(lat, lon, API_KEY)).json()
   
    # Get current weather data
    weather_data = {
        "city": response['name'],
        "temperature": round(response['main']['temp'] - 273.15),
        "feels_like": round(response['main']['feels_like'] - 273.15),
        "description": response['weather'][0]['description'],
        "country": response['sys']['country'],
        "icon": response['weather'][0]['icon']
    }

    # Get forecast for next 7 days
    daily_forecasts = []
    for daily_data in forecast_response['daily'][:7]:
        daily_forecasts.append({
            "day": datetime.datetime.fromtimestamp(daily_data['dt']).strftime("%A"),
            "min_temp": round(daily_data['temp']['min'] - 273.15),
            "max_temp": round(daily_data['temp']['max'] - 273.15),
            "description": daily_data['weather'][0]['description'],
            "icon": daily_data['weather'][0]['icon']
        })

    return weather_data, daily_forecasts