from config import API_KEY, CITY
import requests


def fetch_weather_data():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}"
    try:
        response = requests.get(url, timeout=15)
    except requests.RequestException as exc:
        return {"error": f"Failed to fetch weather data: {exc}"}

    if response.status_code == 200:
        return response.json()
    return {"error": f"Error fetching weather data: {response.status_code}", "details": response.text}
