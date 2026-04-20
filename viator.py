import requests
from datetime import datetime

'''
Notes:
- Some end points have no body.
- Pay attention to API requests using GET, POST, etc.


'''

class ViatorAPI:
    def __init__(self):
        self.api_key = "60f8c17f-b47e-4bbb-9c9f-8a97b7dab528"
        self.base_url = "https://api.viator.com/partner"
        self.headers = {
            "exp-api-key": self.api_key,
            "Accept-Language": "en",
            "Accept": "application/json;version=2.0",
            "Content-Type": "application/json"
        }

    def get_destinations(self):
        url = f"{self.base_url}/destinations"
        
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def search_products(self, destination_id: str, start_date: str, end_date: str, count: int = 3):
        url = f"{self.base_url}/products/search"
        
        body = {
            "filtering": {
                "destination": destination_id,
                "startDate": start_date,
                "endDate": end_date,
                "includeAutomaticTranslations": True,
                "rating": {
                "from": 3,
                "to": 5
                }
            },
            "sorting": {
                "sort": "DEFAULT",
                "order": "DESCENDING"
            },
            "pagination": {
                "start": 1,
                "count": count
            },
            "currency": "USD"
        }
        
        response = requests.post(url, headers=self.headers, json=body)
        data = response.json()
        return data.get("products", [])
    
    def get_product_schedule(self, product_code: str):
        url = f"{self.base_url}/availability/schedules/{product_code}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_sorted_attraction_slots(self, destination_id: str, start_date: str, end_date: str, count: int = 20):
        products = self.search_products(destination_id, start_date, end_date, count=count)
        slots = []

        for product in products:
            product_code = product.get("productCode")
            title = product.get("title")

            if not product_code:
                continue

            try:
                schedule = self.get_product_schedule(product_code)

                # You will need to inspect your actual schedule response shape.
                # This code assumes there is a list of bookable entries somewhere in the response.
                for day in schedule.get("bookableItems", []):
                    travel_date = day.get("date")

                    print(len(day.get("timeSlots", [])))
                    for time_slot in day.get("timeSlots", []):
                        start_time = time_slot.get("startTime")
                        if not travel_date or not start_time:
                            continue

                        dt = datetime.fromisoformat(f"{travel_date}T{start_time}")

                        slots.append({
                            "productCode": product_code,
                            "title": title,
                            "date": travel_date,
                            "startTime": start_time,
                            "datetime": dt,
                            "rawSlot": time_slot,
                        })
                        
            except Exception as e:
                print(f"Error processing {product_code}: {e}")

        slots.sort(key=lambda x: x["datetime"])
        return slots