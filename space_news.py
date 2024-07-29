import requests
import json
from datetime import datetime, timedelta, timezone, date

class SpaceNewsAPI:
    def __init__(self, article_url, report_url: str):
        self.article_url = article_url
        self.report_url = report_url

    def article_query_results(self):
        try:
            query_results = requests.get(self.article_url)
            query_results.raise_for_status()
        except Exception as e:
            print(f"SpaceNewsAPI::article_query_results: Exception has occured: {e}")
            return None
        else:
            self.query_results = query_results.json()
            return self.query_results
    
    def report_query_results(self):
        try:
            query_results = requests.get(self.report_url)
            query_results.raise_for_status()
        except Exception as e:
            print(f"SpaceNewsAPI::report_query_results: Exception has occured: {e}")
            return None
        else:
            self.query_results = query_results.json()
            return self.query_results
        
test = SpaceNewsAPI("https://api.spaceflightnewsapi.net/v4/reports?limit=10", "https://api.spaceflightnewsapi.net/v4/articles?limit=10&is_feature=true")
print(test.article_query_results())
print()
print(test.report_query_results())