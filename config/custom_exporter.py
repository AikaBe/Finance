"""
Custom API Exporter
Example: collecting weather data for Astana (Open-Meteo API)
"""
from prometheus_client import start_http_server, Gauge, Counter, Info
import requests
import time

# === Метрики погоды (Астана) ===
weather_temperature = Gauge('weather_temperature_celsius', 'Current temperature in Astana', ['city', 'country'])
weather_windspeed = Gauge('weather_windspeed_kmh', 'Current wind speed in Astana', ['city', 'country'])
weather_humidity = Gauge('weather_humidity_percent', 'Current humidity in Astana', ['city', 'country'])
weather_pressure = Gauge('weather_pressure_hpa', 'Current pressure in Astana', ['city', 'country'])
weather_precipitation = Gauge('weather_precipitation_mm', 'Current precipitation in Astana', ['city', 'country'])
weather_winddirection = Gauge('weather_winddirection_deg', 'Current wind direction in Astana', ['city', 'country'])

# Метрики состояния API
weather_api_status = Gauge('weather_api_status', 'Weather API status (1=up, 0=down)')
weather_fetch_total = Counter('weather_fetch_total', 'Total API fetch attempts')
weather_fetch_failures = Counter('weather_fetch_failures', 'Total API fetch failures')

# Информационная метрика об экспортере
exporter_info = Info('custom_exporter_info', 'Information about custom exporter')

# === Функция получения данных ===
def fetch_weather_data():
    weather_fetch_total.inc()
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': 51.1694,
            'longitude': 71.4491,
            'current_weather': 'true',
            'timezone': 'Asia/Almaty'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        current = data['current_weather']

        weather_temperature.labels(city='Astana', country='Kazakhstan').set(current['temperature'])
        weather_windspeed.labels(city='Astana', country='Kazakhstan').set(current['windspeed'])
        weather_humidity.labels(city='Astana', country='Kazakhstan').set(current.get('humidity', 0))
        weather_pressure.labels(city='Astana', country='Kazakhstan').set(current.get('pressure', 0))
        weather_precipitation.labels(city='Astana', country='Kazakhstan').set(current.get('precipitation', 0))
        weather_winddirection.labels(city='Astana', country='Kazakhstan').set(current.get('winddirection', 0))

        weather_api_status.set(1)
        return True

    except requests.exceptions.RequestException:
        weather_api_status.set(0)
        weather_fetch_failures.inc()
        return False

# === Главный блок запуска ===
if __name__ == '__main__':
    exporter_info.info({'version': '1.0', 'author': 'Student', 'sources': 'Open-Meteo API'})
    start_http_server(8000)  # Порт 8000 для Prometheus
    print("✅ Custom API exporter started on port 8000")

    while True:
        fetch_weather_data()
        time.sleep(20)  # обновление каждые 20 секунд
