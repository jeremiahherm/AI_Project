from viator import ViatorAPI
from tools import get_tour_info_tool, get_crowd_score_tool, get_value_score_tool
import json

def find_city_destination(data, city_name):
    city_name = city_name.strip().lower()

    for destination in data.get("destinations", []):
        # print(destination.get("name", "").strip().lower())
        if destination.get("name", "").strip().lower() == city_name.strip().lower():
            return destination

    return None

def test(city_name):
    api = ViatorAPI()
    
    # destinations = api.get_destinations()
    # city_destination = find_city_destination(destinations, city_name)
    
    start_date = "2026-10-10"
    end_date = "2026-10-20"
    print(get_tour_info_tool.forward(destination_name=city_name, start_date=start_date, end_date=end_date))
    
    # attractions = api.search_products(destination_id = city_destination.get("destinationId"), start_date = start_date, end_date = end_date)
    
    # print(len(attractions))
    # print(attractions[0]["productUrl"])
    # schedule = api.get_product_schedule(attractions[0]["productCode"])
    # print(schedule)
    # print(attractions[0]["productCode"])
    # print(api.get_sorted_attraction_slots(city_destination.get("destinationId"), start_date, end_date))
    try:
        with open('reviews/reviews.txt', 'r', encoding='utf-8') as file:
            school_reviews = json.load(file)
        total_sentiment = 0
        total_reviews = 0
        for review in school_reviews:
            if "snippet" in review:
                text_to_read = review["snippet"]
                
                user_name = review.get("user", {}).get("name", "Unknown User")
                
                final_judgment = get_crowd_score_tool.forward(text_to_read, review["rating"])
                
                print(f"Review by {user_name}:")
                print(final_judgment)
                print("--------------------------------------------------")
                total_sentiment += final_judgment
                total_reviews += 1
        avg_sentiment = total_sentiment / total_reviews
        price = 10
        print(get_value_score_tool(avg_sentiment, price))
        print(avg_sentiment)
                
                
    except FileNotFoundError:
        print("Couldn't find reviews.txt")
    except json.JSONDecodeError:
        print("reviews.txt not formatted properly")


if __name__ == "__main__":
    test("Paris")