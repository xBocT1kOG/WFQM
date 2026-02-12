import os
from OWM_functions import *

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

# send data to TG:
try:
    today_weather = get_weather_from_db('now', FORCAST_TABLE)
    past_forecast_weather = get_weather_from_db('past', FORCAST_TABLE)
    past_real_weather = get_weather_from_db('past', CURRENT_TABLE)
    message = get_text_forecast(today_weather, past_forecast_weather, past_real_weather)
    send_tg_msg(TOKEN, CHAT_ID, message)
except Exception as e:
    print(f'TG message script failed, {e}')
    send_tg_msg(TOKEN, CHAT_ID, f'TG message script failed, {e}')

# delete data older than two weeks:
try:
    delete_old_data(FORCAST_TABLE)
    delete_old_data(CURRENT_TABLE)
except Exception as e:
    print(f'delete script failed, {e}')
    send_tg_msg(TOKEN, CHAT_ID, f'delete script failed, {e}')