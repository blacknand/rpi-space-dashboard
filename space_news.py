import requests
import json
from datetime import datetime, timedelta, timezone, date

class SpaceNewsAPI:
    def __init__(self, article_url, report_url: str):
        self.article_url = article_url
        self.report_url = report_url
        self.filtered_results = None

    def get_query_results(self, url=None, type_=None):
        try:
            if url is None and type_ == "article":
                url = self.article_url
            elif url is None and type_ == "report":
                url = self.report_url
            query_results = requests.get(self.url)
            query_results.raise_for_status()
        except Exception as e:
            print(f"SpaceNewsAPI::article_query_results: Exception has occured: {e}")
            return None
        else:
            self.query_results = query_results.json()
            return self.query_results
        
    def get_all_results(self, type_=None):
        all_results = []
        if type_ == "article":
            next_url = self.article_url
        else:
            next_url = self.report_url
        while next_url:
            next_results = self.get_query_results(next_url, type_)
            if not next_results:
                quit()

            all_results.extend(next_results["results"])
            next_url = next_results.get("next")
        
        self.query_results = {"results": all_results}
        return self.query_results
    
    def get_filtered_results(self, type_=None):
        if self.query_results is None:
            self.query_results = self.get_all_results(type_)
        
        self.filtered_results = [
            {
                "title": result["title"],
                "url": result["url"],
                "image_url": result["image_url"],
                "news_site": result["news_site"],
                "summary": result["summary"],
                "published": result["published_at"]
            }
            for result in self.query_results["results"]
        ]
        return self.filtered_results
    

        
test = SpaceNewsAPI("https://api.spaceflightnewsapi.net/v4/reports?limit=10", "https://api.spaceflightnewsapi.net/v4/articles?limit=10&is_feature=true")
print(test.article_get_query_results())
print()
print(test.report_get_query_results())