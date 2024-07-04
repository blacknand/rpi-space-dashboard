"""
Uses the LL2 API to get upcoming rocket launches
https://ll.thespacedevs.com/2.2.0/swagger/#/launch/launch_upcoming_list
"""

import requests
import json
import sys

class RocketLaunchesData:
    def __init__(self, query_url: str):
        self.query_url = query_url
        self.query_results = None                                           # Initial state

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
        # filtered_data = {launch_key: self.query_results["results"]} 
        pass

    def json_test_filter(self, json_file: str) ->json:
        open_json_file = open(json_file)
        json_data = json.load(open_json_file)
        json_data = json.dumps(json_data)                                       # Convert to dict to handle null values
        return {self.catch_json_error(lambda: json_data["results"][key]) for key in json_data["results"]}


    # https://stackoverflow.com/questions/27140090/how-can-json-data-with-null-value-be-converted-to-a-dictionary
    def catch_json_error(func, *args, handle=lambda e : e, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return handle(e)

launch_base_url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/"
filters = "limit=25&include_suborbital=true&hide_recent_previous=true&ordering=net&mode=list&tbd=true"
test_url = f"{launch_base_url}?{filters}"

test_obj = RocketLaunchesData(test_url)
test_results = test_obj.json_test_filter(sys.argv[1])
# print(test_obj.catch_json_error(test_results))


# query_results = rocket_query_results(test_url)
# if not query_results:
#     quit()                                          # TODO: Thorough error handling

# with open('ll2data.json', 'w', encoding='utf-8') as f:
#     json.dump(query_results, f, ensure_ascii=False, indent=4)

# for result in query_results["results"]:
#     # print(f"{result["name"]}\n\n")
#     print(f"{result}\n\n\n\n\n")

print(sys.argv[1])