import os
import requests
from dotenv import load_dotenv

load_dotenv()

ODESA_LAT = 46.48
ODESA_LON = 30.73

BASE_URL = 'https://api.openweathermap.org/data/2.5/forecast'

def get_forecast_weather_owm(lat: float, lon: float):

    api_key = os.getenv('OWM_API_KEY')

    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
        "lang": "en"
    }

    try:
        response = requests.get(BASE_URL, params=params)

        # Проверка статуса ответа (200 OK)
        if response.status_code == 200:
            print("<- Успешно получен ответ (200 OK).")
            return response.json()

        # Обработка ошибок API (например, неверный ключ 401, или другие ошибки)
        else:
            print(f"<- Ошибка API: Код статуса {response.status_code}.")
            print(f"   Сообщение: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        # Обработка сетевых ошибок (нет интернета, таймаут и т.п.)
        print(f"<- Сетевая ошибка при запросе к OWM: {e}")
        return None

if __name__ == "__main__":

    weather_data = get_forecast_weather_owm(ODESA_LAT, ODESA_LON)

    if weather_data:
        for i in weather_data['list']:
            print(i['dt_txt'], i['main']['temp'])
            print(i['dt_txt'], i['main']['pressure'])
            print(i['dt_txt'], i['weather'][0]['description'])
            print(i['dt_txt'], i['wind']['speed'], '\n')
