import requests
import json

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


# launch_base_url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/"
# filters = "limit=25&include_suborbital=true&hide_recent_previous=true&ordering=net&mode=list&tbd=true"
# test_url = f"{launch_base_url}?{filters}"


# query_results = rocket_query_results(test_url)
# if not query_results:
#     quit()                                          # TODO: Thorough error handling

# with open('ll2data.json', 'w', encoding='utf-8') as f:
#     json.dump(query_results, f, ensure_ascii=False, indent=4)

# for result in query_results["results"]:
#     # print(f"{result["name"]}\n\n")
#     print(f"{result}\n\n\n\n\n")

