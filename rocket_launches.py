import requests
import json
import requests
from datetime import datetime, timedelta

launch_base_url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/"
# upcoming_launch_request = requests.get(f"{launch_base_url}upcoming/")
    
filters = "limit=10&include_suborbital=true&hide_recent_previous"
test_url = f"{launch_base_url}?{filters}"
print(f"Test URL: {test_url}")

def rocket_query_results(query_url: str) -> dict or None:
    try:
        query_results = requests.get(query_url)
    except Exception as e:
        print(f"Exception has occured: {e}")
    else:
        query_status = query_results.status_code
        print(f"Response status code: {query_status}")
        if query_status != 200:
            return
        return query_results.json()
    
query_results = rocket_query_results(test_url)
if not query_results:
    quit()

print(query_results)