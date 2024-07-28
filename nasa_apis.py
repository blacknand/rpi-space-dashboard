from dotenv import load_dotenv
import requests
import json
import os
import importlib.util
import sys

load_dotenv("keys.env")

# Setup relative path to the directory containing module
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'apod-api'))

# Add the directory to the Python path
sys.path.append(dir_path)

# Define the module name and file path
module_name = 'apod_object_parser'
file_path = os.path.join(dir_path, 'apod_parser', 'apod_object_parser.py')

# Load the module
spec = importlib.util.spec_from_file_location(module_name, file_path)
apod_object_parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apod_object_parser)

class NASAapis:
    def __init__(self):
        pass

    def apod_query(self):
        apod_response = apod_object_parser.get_data(os.environ.get("nasa_key"))
        apod_date = apod_object_parser.get_date(apod_response)
        apod_title = apod_object_parser.get_title(apod_response)
        apod_explanation = apod_object_parser.get_explanation(apod_response)
        apod_url = apod_response.get_url(apod_response)
        return [apod_date, apod_title, apod_explanation, apod_url]

nasa_api_obj = NASAapis()
nasa_api_obj.apod_query()