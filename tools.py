import os
import math
import re
from tavily import TavilyClient
from smolagents import Tool
from viator import ViatorAPI
from transformers import pipeline, AutoTokenizer
import torch


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
            "productCode": tour["productCode"],
            "price": tour["pricing"]["summary"]["fromPrice"]
        } for tour in tours]

# To be used with value score, not final decision. Only used for getting sentiment analysis of user reviews and mapping it to a number. Uses
# multiple models to do so.
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
        # Models are not loaded here — they load on first call to forward()
        self.sentiment_reader = None
        self.score_map = {
            'Very Negative': 0,
            'Negative': 1,
            'Neutral': 2,
            'Positive': 3,
            'Very Positive': 4
        }
        self.labels_map = {value: text for text, value in self.score_map.items()}

    # def _load_models(self):
    #     if self.sentiment_reader is None:
    #         self.sentiment_reader = pipeline(
    #             "sentiment-analysis",
    #             model="tabularisai/multilingual-sentiment-analysis"
    #         )
    #     if self.sentiment_reader2 is None:
    #         self.sentiment_reader2 = pipeline(
    #             "sentiment-analysis",
    #             model="Krish623/sentiment-model",
    #             use_fast=False,
    #             device_map=None,        # Added by Hamad - might need to remove
    #             torch_dtype="auto",     # Added by Hamad - might need to remove
    #             low_cpu_mem_usage=False # Added by Hamad - might need to remove
    #         )

    def _load_models(self):
        if self.sentiment_reader is None:
            self.sentiment_reader = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                use_fast=False,
                device=0 if torch.cuda.is_available() else -1,
            )

    def forward(self, review_text: str, rating: float) -> int:
        self._load_models()

        result = self.sentiment_reader(review_text)[0]
        label = result['label'].lower()  # normalize to lowercase
        score = result['score']
        
        # Map sentiment label to score (distilbert returns POSITIVE/NEGATIVE)
        if 'positive' in label:
            sentiment_score = 3 if score > 0.8 else 2
        elif 'negative' in label:
            sentiment_score = 1 if score > 0.8 else 2
        else:
            sentiment_score = 2

        # Combine sentiment score with rating
        if rating > 0:
            rating = rating - 1

        final_calc = (sentiment_score + rating) / 2
        if (math.ceil(final_calc) - final_calc) <= 0.5:
            final_calc = math.ceil(final_calc)
        else:
            final_calc = math.floor(final_calc)

        return final_calc


# IMPORTANT: use this for the decision making, this will be used for the ultimate display and decision of what the best tour available is
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
        # return the value score (1 - not worth it, 2 - get what you're paying, 3 - Worth the money, 4 - Great value and worth it)
        if average_sentiment >= 4 and price < 100:
            return 4
        elif average_sentiment <= 2 and price > 100:
            return 1
        elif average_sentiment >= 3:
            return 3
        else:
            return 2


get_tour_info_tool = get_tour_info()
get_crowd_score_tool = get_crowd_score()
get_value_score_tool = get_value_score()
