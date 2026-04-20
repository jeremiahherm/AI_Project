import os
import math
import re
from tavily import TavilyClient
from smolagents import Tool
from viator import ViatorAPI
from transformers import pipeline
from smolagents import Tool


class get_tour_info(Tool):
    name = "get_tour_info"
    description = "Gets a list of tour information for a given city and date range."
    inputs = {
        "destination_name": {
            "type": "string",
            "description": "The destination city."
        },
        "start_date": {
            "type": "string",
            "description": "The start date for the tour search in format YYYY-MM-DD."
        },
        "end_date": {
            "type": "string",
            "description": "The end date for the tour search in format YYYY-MM-DD."
        }
    }
    output_type = "array"
    
    def forward(self, destination_name: str, start_date: str, end_date: str) -> list:
        api = ViatorAPI()
        data = api.get_destinations()
        destination_name = destination_name.strip().lower()
        
        destination_info = None

        for destination in data.get("destinations", []):
            if destination.get("name", "").strip().lower() == destination_name.strip().lower():
                destination_info = destination
                break
        if not destination_info:
            raise ValueError(f"Destination '{destination_name}' not found.")
        
        destination_id = destination_info.get("destinationId")
        tours = api.search_products(destination_id, start_date, end_date)
        
        return [{
                    "title": tour["title"],
                    "description": tour["description"],
                    "url": tour["productUrl"],
                    "productCode": tour["productCode"]
                } for tour in tours]

class get_crowd_score(Tool):
    name = "get_crowd_score"
    description = "Reads a review to understand the customers' feelings and returns a sentiment score"
    inputs = {
        "review_text": {
            "type": "string",
            "description": "The text of the review to analyze."
        },
        "rating": {
            "type": "number",
            "description": "The number of stars the reviewer gave the experience."
        }
    }
    output_type = "integer"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sentiment_reader = pipeline(
            "sentiment-analysis",
            model="tabularisai/multilingual-sentiment-analysis"
        )
        self.sentiment_reader2 = pipeline(
            "sentiment-analysis",
            model="Krish623/sentiment-model"
        )

        self.score_map = {
            'Very Negative': 0,
            'Negative': 1,
            'Neutral': 2,
            'Positive': 3,
            'Very Positive': 4
        }
        
        self.labels_map = {value: text for text, value in self.score_map.items()}
    
    def forward(self, review_text: str, rating: float) -> int:
        result1 = self.sentiment_reader(review_text)[0]
        result2 = self.sentiment_reader2(review_text)[0]

        label1 = result1['label']
        label2 = result2['label']
        
        score1 = self.score_map.get(label1, 2)
        score2 = self.score_map.get(label2, 2)

        average_score = (score1 + score2) / 2
        final_score = math.ceil(average_score)
        if rating > 0:
            rating = rating - 1

        final_calc = (final_score + rating) / 2
        if (math.ceil(final_calc) - final_calc) <= 0.5:
            final_calc = math.ceil(final_calc)
        else:
            final_calc = math.floor(final_calc)
        #final_label = self.labels_map.get(final_calc, "Unknown")

        return final_calc

class get_value_score(Tool):
    name = "get_value_score"
    description = "Reads the price of a tour and compares it to the user reviews to determine if the tour is good value on a scale from 1-4 (1 - not worth it, 2 - get what you're paying, 3 - Worth the money, 4 - Great value and worth it)."
    inputs = {
        "price": {
            "type": "number",
            "description": "The cost of the tour."
        },
        "average_sentiment": {
            "type": "number",
            "description": "The average sentiment of the user reviews. (e.g., 0 - Very Negative, 1 - Negative, 2 - Neutral, 3 - Positive, 4 - Very Positive)"
        }
    }
    output_type = "integer"

    def forward(self, price: float, average_sentiment: float):
        #sentiment_map = {
         #    0: 'Very Negative',
          #   1: 'Negative',
           #  2: 'Neutral',
            # 3: 'Positive',
            # 4: 'Very Positive'
        #}
        #sentiment_rank = sentiment_map.get(average_sentiment, "Unknown")
        # return the value score (1 - not worth it, 2 - get what you're paying, 3 - Worth the money, 4 - Great value and worth it)
        if average_sentiment >= 4 and price < 100:
            return 4
        elif average_sentiment <= 2 and price > 150:
            return 1
        elif average_sentiment >= 3:
            return 3
        else:
            return 2

get_tour_info_tool = get_tour_info()
get_crowd_score_tool = get_crowd_score()
# get_value_score_tool = get_value_score()
