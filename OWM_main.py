import os
from OWM_functions import *
import datetime
import pytz

# load secrets:
api_key = os.getenv("OWM_API_KEY") #API key for weather service
url = os.environ.get("SUPABASE_URL") #URL to DB
key = os.environ.get("SUPABASE_KEY") #key for DB
TOKEN = os.environ.get("TOKEN") #TG_bot token
CHAT_ID = os.environ.get("CHAT_ID") #TG_chat ID

# city coordinates:
ODESA_lat = 46.48
ODESA_lon = 30.73

# URL for OnlineWeatherMap API connect:
URL_current_weather = "https://api.openweathermap.org/data/2.5/weather"
URL_forecast_weather = "https://api.openweathermap.org/data/2.5/forecast"

# time zone for Ukraine:
TIMEZONE = 'Europe/Kyiv'

# tables for upload
CURRENT_TABLE = 'owm_current'
FORCAST_TABLE = 'owm_forecast'

# gather current weather:
raw_data = get_weather(ODESA_lat, ODESA_lon, URL_current_weather)
clear_data = get_data(raw_data)
upload_data(clear_data, CURRENT_TABLE)
send_tg_msg(TOKEN, CHAT_ID, f'weather gathered {datetime.datetime.now(tz=pytz.timezone(TIMEZONE))}')

# gather forecast weather:
raw_data = get_weather(ODESA_lat, ODESA_lon, URL_forecast_weather)
clear_data = get_data(raw_data)
upload_data(clear_data, FORCAST_TABLE)
send_tg_msg(TOKEN, CHAT_ID, f'forecast gathered {datetime.datetime.now(tz=pytz.timezone(TIMEZONE))}')

