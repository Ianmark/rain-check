""" Get location of current user via ip address"""
import requests, os

from dotenv import load_dotenv
from django.contrib.gis.geoip2 import GeoIP2

# Configuration settings
load_dotenv()
API_KEY = os.getenv('GEOLOCATE_API_KEY')

api_url = 'https://ipgeolocation.abstractapi.com/v1/?api_key=' + API_KEY

def get_location_from_ip_address(request):

    # Get user IP address
    remote_addr = request.META.get('HTTP_X_FORWARDED_FOR')
    if remote_addr:
        ip_address = remote_addr.split(',')[-1].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    # Get country_code
    response = requests.get(api_url).json() 
    '''+ "&ip_address=" + ip_address'''

    return response['latitude'], response['longitude']

def get_lat_and_lon_from_city(city, API_KEY):
    response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}").json()
    
    lat, lon = response[0]['lat'], response[0]['lon']
    return lat, lon