import os
import pandas as pd
import requests
from dotenv import load_dotenv
import datetime
import pytz
import math
from supabase import create_client, Client
import telebot
import urllib.parse
import random

# load secrets:
load_dotenv()
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

# telegram names:
TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_ID")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# define function to convert unix(UTC) to local time:
def convert_unix(unix_ts: int, timezone_name: str = TIMEZONE):
    utc_datetime = datetime.datetime.fromtimestamp(unix_ts, tz=pytz.utc)
    tz = pytz.timezone(timezone_name)
    local_datetime = utc_datetime.astimezone(tz)
    formated_time = local_datetime.strftime('%Y-%m-%d %H:%M:%S')

    return formated_time

# define function to get current weather data:
def get_weather(lat: float, lon: float, url: str) -> dict | None:

    if not api_key:
        print('API Load Error') #ADD ALERT!!!
        return None

    # parameters for API data:
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'metric',
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json()

        else:
            print(f"API Error: Code {response.status_code}.")
            print(f"Message: {response.text}") #ADD ALERT!!!
            return None

    except requests.exceptions.RequestException as e:
        print(f"Fail to connect to OWM: {e}") #ADD ALERT!!!
        return None

# define function to get clear data from json:
def get_data(raw_data: dict) -> pd.DataFrame:

    # create dict for data gather:
    clear_data = dict()

    # fill data dict:
    columns = ['date', 'time', 'city', 'weather', 'description', 'clouds_%',
               'temp', 'temp_min', 'temp_max', 'feels_like', 'humidity',
               'pressure', 'pressure_ground_level', 'pressure_sea_level',
               'wind', 'wind_gust', 'visibility_m']

    for col in columns:
        clear_data[col] = list()

    if 'list' in raw_data:

        for data in raw_data['list']:
            clear_data['date'].append(convert_unix(int(data['dt'])))
            clear_data['time'].append(convert_unix(int(data['dt'])))
            clear_data['weather'].append(data['weather'][0]['main'])
            clear_data['description'].append(data['weather'][0]['description'])
            clear_data['clouds_%'].append(data['clouds']['all'])
            clear_data['temp'].append(data['main']['temp'])
            clear_data['temp_min'].append(data['main']['temp_min'])
            clear_data['temp_max'].append(data['main']['temp_max'])
            clear_data['feels_like'].append(data['main']['feels_like'])
            clear_data['humidity'].append(data['main']['humidity'])
            clear_data['pressure'].append(data['main']['pressure'])
            clear_data['pressure_ground_level'].append(data['main']['grnd_level'])
            clear_data['pressure_sea_level'].append(data['main']['sea_level'])
            clear_data['wind'].append(data['wind']['speed'])
            clear_data['wind_gust'].append(data['wind']['gust'])
            try:
                clear_data['visibility_m'].append(raw_data['visibility'])
            except KeyError as e:
                clear_data['visibility_m'].append(None)
                send_tg_msg(TOKEN, CHAT_ID,f'visibility data receive failed, {e}')

        for i in range(len(raw_data['list'])):
            clear_data['city'].append(raw_data['city']['name'])

    else:
        clear_data['date'].append(convert_unix(int(raw_data['dt'])))
        clear_data['time'].append(convert_unix(int(raw_data['dt'])))
        clear_data['city'].append(raw_data['name'])
        clear_data['weather'].append(raw_data['weather'][0]['main'])
        clear_data['description'].append(raw_data['weather'][0]['description'])
        clear_data['clouds_%'].append(raw_data['clouds']['all'])
        clear_data['temp'].append(raw_data['main']['temp'])
        clear_data['temp_min'].append(raw_data['main']['temp_min'])
        clear_data['temp_max'].append(raw_data['main']['temp_max'])
        clear_data['feels_like'].append(raw_data['main']['feels_like'])
        clear_data['humidity'].append(raw_data['main']['humidity'])
        clear_data['pressure'].append(raw_data['main']['pressure'])
        clear_data['pressure_ground_level'].append(raw_data['main']['grnd_level'])
        clear_data['pressure_sea_level'].append(raw_data['main']['sea_level'])
        clear_data['wind'].append(raw_data['wind']['speed'])
        clear_data['wind_gust'].append(raw_data['wind']['gust'])
        try:
            clear_data['visibility_m'].append(raw_data['visibility'])
        except KeyError as e:
            clear_data['visibility_m'].append(None)
            send_tg_msg(TOKEN, CHAT_ID, f'visibility data receive failed, {e}')


    # convert data to DataFrame:
    clear_data_df = pd.DataFrame(clear_data)

    # convert datetime format
    clear_data_df['date'] = pd.to_datetime(clear_data['date'])
    clear_data_df['time'] = pd.to_datetime(clear_data['date'])
    clear_data_df['date'] = clear_data_df['date'].dt.ceil('h')
    clear_data_df['time'] = clear_data_df['date'].dt.ceil('h')
    clear_data_df['date'] = clear_data_df['date'].dt.date
    clear_data_df['time'] = clear_data_df['time'].dt.time

    # round temperature and wind values:
    round_columns = ['temp', 'temp_min', 'temp_max', 'feels_like', 'wind', 'wind_gust']
    for col in round_columns:
        clear_data_df[col] = clear_data_df[col].apply(math.floor)

    # convert objects to string:
    obj_columns = ['city', 'weather', 'description']
    for col in obj_columns:
        clear_data_df[col] = clear_data_df[col].astype(pd.StringDtype())

    return clear_data_df

# define function to upload data to DB:
def upload_data(data: pd.DataFrame, table_name: str) -> None:

    # convert DataFrame to dict(json):
    data['date'] = data['date'].dt.strftime('%Y-%m-%d')
    data['time'] = data['time'].dt.strftime('%H:%M:%S')

    upload_dict = data.to_dict(orient='records')

    # connection setup
    supabase = create_client(url, key)

    # insert data:
    response = (
        supabase.table(table_name)
        .upsert(upload_dict, on_conflict='date')
        .execute()
    )
    return None

# define telegram function:
def send_tg_msg(token:str, chat_id: str, msg: str) -> None:

    bot = telebot.TeleBot(token)
    bot.send_message(chat_id, msg, parse_mode='HTML')

def send_tg_image(token: str, chat_id: str, image: str) -> None:
    bot = telebot.TeleBot(token)
    with open(image, 'rb') as photo:
        bot.send_photo(chat_id, photo, parse_mode='HTML')

#if __name__ == '__main__':
