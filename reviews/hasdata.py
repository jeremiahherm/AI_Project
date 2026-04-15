import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("HASDATA_API_KEY")
reviews_url = os.getenv("HASDATA_REVIEWS_URL")
search_url = os.getenv("HASDATA_SEARCH_URL")

class HasDataAPI:        
    # STEP 1: Use Google Maps API to get placeId for query
    def get_place_id(self, location: str):
        if location is None or '':
            raise ValueError("Location cannot be empty or None.")

        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }

        params = {
            'q': location
        }

        response = requests.get(search_url, headers=headers, params=params)

        if response.status_code != 200:
            print("Error fetching place ID:", response.status_code, response.text)
            raise RuntimeError("Failed to fetch place ID")

        data = response.json()
        
        return data['placeResults']

    # STEP 2: Use Google Maps Reviews API to get 10 reviews ONLY
    def get_reviews(self, place_id: str, count: int=5):
        if place_id is None or '':
            raise ValueError("Place ID cannot be empty or None.")

        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }

        params = {
            'placeId': place_id,
            'reviewsLimit': count
        }

        response = requests.get(reviews_url, headers=headers, params=params)

        if response.status_code != 200:
            print("Error fetching reviews:", response.status_code, response.text)
            raise RuntimeError("Failed to fetch reviews")

        data = response.json()
        
        return data.get('reviews', [])
       


# Example usage
api = HasDataAPI()

location = api.get_place_id("ExperienceFirst")
reviews = api.get_reviews(location['placeId'])
print(reviews)
