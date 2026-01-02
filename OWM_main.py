import os
from OWM_functions import *
from supabase import create_client, Client

# load secrets:
api_key = os.getenv("OWM_API_KEY") #API key for weather service
url = os.environ.get("SUPABASE_URL") #URL to DB
key = os.environ.get("SUPABASE_KEY") #key for DB

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

# gather forecast weather:
# get current date rounded
current_date = datetime.datetime.now(pytz.timezone(TIMEZONE))
rounded_date = current_date.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)

# get last date from DB +3 hours
supabase: Client = create_client(url, key)

response = (
    supabase.table(FORCAST_TABLE)
    .select("date")
    .order("date", desc=True)
    .limit(1)
    .execute()
)
if not response.data:
    last_date = None

else:
    last_date_str = response.data[0]['date'].replace('T', ' ')
    last_date = datetime.datetime.strptime(last_date_str, '%Y-%m-%d %H:%M:%S')

# compare dates for gathering:
if last_date == rounded_date or last_date is None:
    raw_data = get_weather(ODESA_lat, ODESA_lon, URL_forecast_weather)
    clear_data = get_data(raw_data)
    upload_data(clear_data, FORCAST_TABLE)

