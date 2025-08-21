import os
from dotenv import load_dotenv
import pandas as pd
import requests

load_dotenv()

class NewsFetcher:
    def __init__(self):
        self.api = os.getenv("API_KEY")
        self.base_url = "https://newsapi.org/v2/everything"
        self.data = None
        self.df = None

    def fetch_data(self, query="tesla", from_date=None, source=None):
        params = {
            "q": query,
            "apiKey": self.api,
            "sortBy": "publishedAt",
        }
        if from_date:
            params["from"] = from_date
        if source:
            params["sources"] = source

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            self.data = response.json()
            if "articles" in self.data:
                self.df = pd.DataFrame(self.data["articles"])
            else:
                self.df = None
        except Exception as e:
            print(f"❌ API Request Failed: {e}")
            self.df = None

    def save_to_csv(self, filename="News_data.csv"):
        if self.df is not None:
            self.df.to_csv(filename, index=False)
            print(f"✅ Data saved to {filename}")
        else:
            print("❌ No DataFrame to save. Fetch data first.")
