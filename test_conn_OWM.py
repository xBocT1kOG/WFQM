import os
import requests
from dotenv import load_dotenv  # Необходима для локальной работы в PyCharm

# --- 1. Настройка и Константы ---

# Загружаем переменные окружения из .env (нужно только для локального запуска)
# В GitHub Actions этот вызов не нужен, так как переменные уже загружены.
load_dotenv()

# Координаты Одессы, Украина
ODESA_LAT = 46.48
ODESA_LON = 30.73

# Базовый URL для текущей погоды OWM
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


# --- 2. Функция Получения Данных ---

def get_current_weather_owm(lat: float, lon: float) -> dict | None:
    """
    Получает текущую погоду от OpenWeatherMap по координатам.

    :param lat: Широта.
    :param lon: Долгота.
    :return: Словарь с данными погоды в формате JSON или None в случае ошибки.
    """
    # ⚠️ Чтение ключа из переменной окружения (OWM_API_KEY)
    api_key = os.getenv("OWM_API_KEY")

    if not api_key:
        print("Ошибка: Переменная окружения 'OWM_API_KEY' не найдена.")
        return None

    # Формирование параметров запроса
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",  # Для получения температуры в Цельсиях
        "lang": "en"  # Для русскоязычного описания погоды
    }

    print(f"-> Запрос к OWM по координатам ({lat}, {lon})...")

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


# --- 3. Пример Использования (для проверки) ---

if __name__ == "__main__":
    # Предполагается, что вы создали файл .env с ключом OWM_API_KEY

    weather_data = get_current_weather_owm(ODESA_LAT, ODESA_LON)

    if weather_data:
        # Вывод только ключевых полей для демонстрации
        temp_c = weather_data['main']['temp']
        pressure = weather_data.get('main', {}).get('pressure')
        description = weather_data.get('weather', [{}])[0].get('description')
        wind_speed = weather_data.get('wind', {}).get('speed')

        print("\n=== Полученные Данные OWM (Одесса) ===")
        print(f"Температура: {temp_c}°C")
        print(f"Давление: {pressure} гПа")
        print(f"Описание: {description}")
        print(f"Скорость ветра: {wind_speed} м/с")
    else:
        print("\nНе удалось получить данные о погоде.")