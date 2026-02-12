import os
import pandas as pd
import requests
from dotenv import load_dotenv
import datetime
import pytz
import math
from supabase import create_client, Client
import telebot
from google import genai

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
def convert_unix(unix_ts: int, timezone_name: str = TIMEZONE) -> str:
    utc_datetime = datetime.datetime.fromtimestamp(unix_ts, tz=pytz.utc)
    tz = pytz.timezone(timezone_name)
    local_datetime = utc_datetime.astimezone(tz)
    formated_time = local_datetime.strftime('%Y-%m-%d %H:%M:%S')

    return formated_time

# define function to get current weather data:
def get_weather(lat: float, lon: float, url: str) -> dict | None:

    if not api_key:
        print('API Load Error')
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
               'wind', 'wind_gust']

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

    # convert data to DataFrame:
    clear_data_df = pd.DataFrame(clear_data)

    # convert datetime format
    clear_data_df['date'] = pd.to_datetime(clear_data['date'])
    clear_data_df['date'] = clear_data_df['date'].dt.ceil('h')
    clear_data_df['date'] = clear_data_df['date'].dt.date
    clear_data_df['time'] = pd.to_datetime(clear_data['time'])
    clear_data_df['time'] = clear_data_df['time'].dt.ceil('h')
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
    data['date'] = data['date'].astype(str)
    data['time'] = data['time'].astype(str)

    # convert DataFrame to JSON:
    upload_dict = data.to_dict(orient='records')

    # connection setup
    supabase = create_client(url, key)

    # insert data with UPSERT:
    response = (
        supabase.table(table_name)
        .upsert(upload_dict, on_conflict='date, time')
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

# define get data from DB, date = 'now'/'past':
def get_weather_from_db(date: str, table: str) -> pd.DataFrame:
    today = datetime.date.today()
    day_0 = today.strftime("%Y-%m-%d")
    day_1 = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    day_2 = (today - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    day_3 = (today - datetime.timedelta(days=3)).strftime("%Y-%m-%d")

    supabase: Client = create_client(url, key)

    if date == 'now':
        days = [day_0]

    elif date == 'past':
        days = [day_1, day_2, day_3]

    else:
        raise KeyError('Wrong date parameter, use "now" or "past"')

    response = (
        supabase.table(table)
        .select("*")
        .in_("date", days)
        .execute()
    )

    if not response.data:
        raise ValueError("No data returned from the database.")

    return pd.DataFrame(response.data)

# define AI connect and process data:
def get_text_forecast(today: pd.DataFrame, past_forecast: pd.DataFrame, past_real: pd.DataFrame) -> str:
    today_as_text = today.to_string(index=False)
    past_forecast_as_text = past_forecast.to_string(index=False)
    past_real_as_text = past_real.to_string(index=False)

    prompt = f'''
    Ты — саркастичный, но полезный метеоролог.
    Отвечай в стиле старого одессита, с юмором и местными словечками.
    Вот данные о погоде на сегодня: {today_as_text}
    
    Твоя задача:
    1. Проанализируй данные.
    2. Напиши краткую сводку на русском языке.
    3. Подкрепляй свои слова актуальными значениями погоды из данных.
    4. Нас интересует время: утро, день и вечер.
    5. Если будет дождь, обязательно предупреди.
    6. Если какие то значения погоды выше или ниже общепринятой региональной нормы, отметь это.
    7. Оцени точность прогноза в процентах и скажи, стоит ли доверять прогнозу сегодня.
        Данные по прогнозу погоды за прошлые дни: {past_forecast_as_text}
        Данные по реальной погоде за прошлые дни: {past_real_as_text}
    
    
    Структура ответа, каждый пункт это новый абзац без оглавления:
    1. Приветствие (одно предложение, максимум 10 слов. Отметь какой сегодня день недели).
    2. Краткий прогноз погоды на сегодня (Утро, день, вечер. Только температура и осадки.
        Каждое предложение с новой строчки. Выделяй температуру и осадки тегом <b>...</b>.
        Пример: Утром <b>+2°C</b>).
    3. Сводка прогноза погоды на сегодня с конкретными значениями (Максимум 100 слов. 
        Выделяй температуру и осадки тегом <b>...</b>.Пример: Утром <b>+2°C</b>).
    4. Оценка точности прогноза на основе анализа прошлых данных (1-2 предложения, максимум 20 слов).
    5. Прощание (Одно предложение, максимум 10 слов).
    '''
    with genai.Client(api_key=GEMINI_API_KEY) as client:

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text

#define func to delete data older than 2 weeks:
def delete_old_data(table: str) -> None:
    today = datetime.datetime.today()
    delete_date = (today - datetime.timedelta(weeks=2)).strftime("%Y-%m-%d")

    supabase: Client = create_client(url, key)

    response = (
        supabase.table(table)
        .delete()
        .lte("date", delete_date)
        .execute()
    )

if __name__ == '__main__':
    today_weather = get_weather_from_db('now', FORCAST_TABLE)
    past_forecast_weather = get_weather_from_db('past', FORCAST_TABLE)
    past_real_weather = get_weather_from_db('past', CURRENT_TABLE)
    message = get_text_forecast(today_weather, past_forecast_weather, past_real_weather)
    print(message)