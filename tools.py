from smolagents import Tool
from viator import ViatorAPI
from transformers import pipeline
from smolagents import DuckDuckGoSearchTool
from reviews import HasDataAPI
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
    
    def forward(self, review_text: str) -> str:
        result1 = self.sentiment_reader(review_text)[0]
        result2 = self.sentiment_reader2(review_text)[0]

        label1 = result1['label']
        label2 = result2['label']
        
        score1 = self.score_map.get(label1, 2)
        score2 = self.score_map.get(label2, 2)

        average_score = (score1 + score2) / 2
        final_score = math.ceil(average_score)
        
        final_label = self.labels_map.get(final_score, "Unknown")

        return f"The crowd sentiment score for this review is: {final_label}."

class SearchTool(Tool):
    name = "SearchTool"
    description = "Searches the web for information related to a query."
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query."
        }
    }
    output_type = "string"

    def forward(self, query: str) -> str:
        search = DuckDuckGoSearchTool()
        result = search(query)
        return result
    
class ReviewsScraper(Tool):
    name="ReviewScraper"
    description="Scrapes reviews for a given location and returns them as a list."
    inputs = {
        "location": {
            "type": "string",
            "description": "The location to scrape reviews for."
        },
        "count": {
            "type": "integer",
            "description": "The number of reviews to return. Defaults to 3 if not provided."
        }
    }

    def forward(self, location: str, count: int=3) -> list:
        api = HasDataAPI()
        place_results = api.get_place_id(location)
        
        if not place_results:
            raise ValueError(f"No place results found for location '{location}'.")

        location = api.get_place_id(location)
        reviews = api.get_reviews(location['placeId'], count=count)
        
        return reviews

get_tour_info_tool = get_tour_info()
get_crowd_score_tool = get_crowd_score()
search_tool = SearchTool()
reviews_scraper_tool = ReviewsScraper()