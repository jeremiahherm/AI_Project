from smolagents import Tool
from viator import ViatorAPI

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


get_tour_info_tool = get_tour_info()