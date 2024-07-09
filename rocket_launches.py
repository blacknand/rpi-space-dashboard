"""
Uses the LL2 API to get upcoming rocket launches
https://ll.thespacedevs.com/2.2.0/swagger/#/launch/launch_upcoming_list
"""

import requests
import json
import sys
from datetime import datetime, timedelta, timezone

class RocketLaunchesData:
    def __init__(self, query_url: str):
        self.query_url = query_url
        self.query_results = None                                  
        self.filtered_results = None
        self.filtered_test_results = None

    def rocket_query_results(self) -> dict or None:
        try:
            query_results = requests.get(self.query_url)
            query_results.raise_for_status()
        except Exception as e:
            print(f"RocketLaunchesData::rocket_query_results: Exception has occured: {e}")
            return None
        else:
            self.query_results = query_results.json()
            return self.query_results
        
    def json_file_dump(self, file: str) -> None:
        self.query_results = self.rocket_query_results()
        if self.query_results is None:
            raise Exception(f"Error writing to {file}. No launch data")

        try:
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(self.query_results, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"RocketLaunchesData::json_file_dump: Exception has occured: {e}")

    def get_filtered_results(self) -> json:
        self.filtered_results = [(result["name"], result["lsp_name"]) for result in self.query_results["results"]]
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
        current_time = datetime.now(timezone.utc)
        updated_results = []
        for i in self.filtered_test_results:
            launch_time = datetime.strptime(i[-1], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            time_difference = launch_time - current_time
            if time_difference.total_seconds() < 0:
                launch_time += timedelta(minutes=15)
                time_difference = launch_time - current_time
            
            updated_results.append({
                "name": i[0],
                "organization": i[1],
                "status": i[2],
                "image": i[3],
                "net": launch_time.isoformat(),
                "countdown": self.format_countdown(time_difference)
            })

        return updated_results

    def format_countdown(self, time_difference):
        days, seconds = time_difference.days, time_difference.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        microseconds = time_difference.microseconds

        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "microseconds": microseconds
        }


launch_base_url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/"
filters = "limit=25&include_suborbital=true&hide_recent_previous=true&ordering=net&mode=list&tbd=true"
test_url = f"{launch_base_url}?{filters}"
test_obj = RocketLaunchesData(test_url)
# test_obj.rocket_query_results()
# test_obj.json_file_dump(sys.argv[1])
# print(test_obj.json_test_filter(sys.argv[1]))
test_obj.json_test_filter(sys.argv[1])
print(test_obj.updated_net())
# print(test_obj.check_request_usage())