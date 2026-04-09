from viator import ViatorAPI
from viator_tools import get_tour_info_tool, get_crowd_score_tool

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
    test_review = "Incredible tour, I loved it more than my own religion. I would lay down my life for another chance of going on this life-changing experience."
    print(get_crowd_score_tool.forward(review_text=test_review))
    


if __name__ == "__main__":
    test("Paris")