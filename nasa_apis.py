from dotenv import load_dotenv
import requests
import json
import os

load_dotenv(".env")
NASA_API_KEY = os.environ.get("NASA_API_KEY")

INSIGHT_API_URL = f"https://api.nasa.gov/insight_weather/?api_key=DEMO_KEY&feedtype=json&ver=1.0"

insight_api_results = requests.get(INSIGHT_API_URL)
insight_api_json = insight_api_results.json()

print(insight_api_json)