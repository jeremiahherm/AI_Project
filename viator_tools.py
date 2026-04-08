from smolagents import Tool
from viator import ViatorAPI
from transformers import pipeline
import math

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
            "description": "The start date for the tour search."
        },
        "end_date": {
            "type": "string",
            "description": "The end date for the tour search."
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
                    "url": tour["productUrl"]
                } for tour in tours]

class get_crowd_score(Tool):
    name = "get_crowd_score"
    description = "Reads a review to understand the customers' feelings and returns a sentiment score"
    inputs = {
        "review_text": {
            "type": "string",
            "description": "The text of the review to analyze."
        }
    }
    output_type = "string"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sentiment_reader = pipeline(
            "sentiment-analysis",
            model="tabularisai/multilingual-sentiment-analysis"
        )
        self.sentiment_reader2 = pipeline(
            "sentiment-analysis",
            model="eakashyap/product-review-sentiment-analyzer"
        )
    
    def forward(self, review_text: str) -> str:
        result1 = self.sentiment_reader(review_text)[0]
        result2 = self.sentiment_reader2(review_text)[0]

        label1 = result1['label']
        label2 = result2['label']
        score1 = 0
        score2 = 0
        if label1 == 'Very Negative':
            score1 = 0
        elif label1 == 'Negative':
            score1 = 1
        elif label1 == 'Neutral':
            score1 = 2
        elif label1 == 'Positive':
            score1 = 3
        elif label1 == 'Very Positive':
            score1 = 3
        
        if label2 == 'Very Negative':
            score2 = 0
        elif label2 == 'Negative':
            score2 = 1
        elif label2 == 'Neutral':
            score2 = 2
        elif label2 == 'Positive':
            score2 = 3
        elif label2 == 'Very Positive':
            score2 = 3

        labels_map = {0: 'Very Negative', 1: 'Negative', 2: 'Neutral', 3: 'Positive', 4: 'Very Positive'}
        label = math.ceil((score1 + score2)/2)
        return f"The crowd sentiment score for this review is: {labels_map[label]}."

get_tour_info_tool = get_tour_info()
get_crowd_score_tool = get_crowd_score()