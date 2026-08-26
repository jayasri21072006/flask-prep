import os

API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
CITY = os.getenv("CITY", "London")
CSV_FILE = os.getenv("CSV_FILE", "weather_data.csv")
EXCEL_FILE = os.getenv("EXCEL_FILE", "weather_data.xlsx")
XML_FILE = os.getenv("XML_FILE", "weather_data.xml")
