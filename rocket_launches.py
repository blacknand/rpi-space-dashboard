import requests
import json
from datetime import datetime, timedelta, timezone, date
import sys
from requests.exceptions import HTTPError, Timeout

class RocketLaunchesData:
    def __init__(self, query_url: str):
        self.query_url = query_url
        self.query_results = None                                  
        self.filtered_results = None
        self.filtered_test_results = None
        self.initial_data = {}

    def rocket_query_results(self, url=None, retries=3) -> dict or None:
        if url is None:
            url = self.query_url
        
        try:
            response = requests.get(url, timeout=50)  
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            if response.status_code == 524 and retries > 0:
                print(f"RocketLaunchesData::rocket_query_results: 524 Server Error: Retrying ({retries} retries left)...")
                return self.rocket_query_results(url, retries - 1)
            else:
                print(f"RocketLaunchesData::rocket_query_results: HTTP error occurred: {http_err}")
        except Timeout:
            print("RocketLaunchesData::rocket_query_results: The request timed out")
        except Exception as err:
            print(f"RocketLaunchesData::rocket_query_results: Other error occurred: {err}")
        return None
        
    def json_file_dump(self, file: str) -> None:
        self.query_results = self.rocket_query_results()
        if self.query_results is None:
            raise Exception(f"Error writing to {file}. No launch data")
        try:
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(self.query_results, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"RocketLaunchesData::json_file_dump: Exception has occured: {e}")

    def get_all_results(self):
        all_results = []
        next_url = self.query_url
        while next_url:
            next_results = self.rocket_query_results(next_url)
            if not next_results:
                sys.exit()
        
            all_results.extend(next_results["results"])
            next_url = next_results.get("next")
        
        self.query_results = {"results": all_results}
        return self.query_results

    def get_filtered_results(self) -> list:
        if self.query_results is None:
            self.query_results = self.get_all_results()
        
        self.filtered_results = [
            {
                "name": result["name"],
                "lsp_name": result["lsp_name"],
                "status": result["status"]["abbrev"],
                "image": result["image"],
                "net": result["net"],
                "mission": result["mission"],
                "mission_type": result["mission_type"],
                "pad": result["pad"],
                "location": result["location"]
            }
            for result in self.query_results["results"]
        ]
        return self.filtered_results

    def json_test_filter(self, json_file: str) -> json:
        # Test querying JSON file to prevent usage of API queries (15 per hour)
        open_json_file = open(json_file)
        json_file_data = json.loads(open_json_file.read())
        self.filtered_test_results = [(result["name"], result["lsp_name"], result["status"]["abbrev"], result["image"], result["net"]) for result in json_file_data["results"]]
        return self.filtered_test_results
    
    def check_request_usage(self) -> json:
        # Check the number of queries made to LL2 API per hour
        try:
            api_throttle_results = requests.get("https://ll.thespacedevs.com/2.2.0/api-throttle/")
            api_throttle_results.raise_for_status()
        except Exception as e:
            print("RocketLaunchesData::check_rocket_usage: Exception has occured: {e}")
            return None
        else:
            return api_throttle_results.json()
        
    def updated_net(self) -> str:
        # Remove launches past T+ 15 minutes
        current_time = datetime.now(timezone.utc)
        updated_results = []
        for result in self.filtered_results:
            launch_time = datetime.strptime(result["net"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            time_difference = launch_time - current_time
            if time_difference.total_seconds() < 0:
                launch_time += timedelta(minutes=15)
                time_difference = launch_time - current_time
            if current_time - launch_time <= timedelta(minutes=15):
                countdown = self.format_countdown(time_difference) 
                updated_results.append({
                    **result,
                    "status": result["status"],
                    "net": launch_time.strftime("%d %B"),
                    "countdown": countdown
                })

        return updated_results

    def format_countdown(self, time_difference):
        days, seconds = time_difference.days, time_difference.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds
        }