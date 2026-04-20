import litellm
from smolagents import LiteLLMModel, CodeAgent, InferenceClientModel
from openai import OpenAI
from reviews.hasdata import HasDataAPI
from viator import ViatorAPI
from tools import get_tour_info_tool, get_crowd_score_tool
import os
from dotenv import load_dotenv
import time
import random
import time
import asyncio

def create_agent(model_id):
    model = LiteLLMModel(
        model_id=model_id,
        api_key=os.getenv("OPENAI_API_KEY"),
        num_retries=3,
    )

    return CodeAgent(
        tools=[get_tour_info_tool, get_crowd_score_tool],
        model=model
    )

def run_with_fallback(prompt, max_rounds=3):
    models = [
        "openai/gpt-5-mini",
        "openai/gpt-4.1-mini",
        "openai/gpt-5-nano",
    ]

    last_error = None

    for round_num in range(max_rounds):
        for model_id in models:
            try:
                print(f"Trying model: {model_id}")
                agent = create_agent(model_id)
                return agent.run(prompt)

            except Exception as e:
                last_error = e
                err_text = str(e).lower()
                print(f"Failed with {model_id}: {e}")

                if "429" in err_text or "too many requests" in err_text:
                    wait = min(60, (2 ** round_num) * 5 + random.uniform(0, 1.5))
                    print(f"Rate limited. Sleeping for {wait:.1f}s")
                    time.sleep(wait)
                    continue

                # Non-rate-limit error: try next model immediately
                continue

    raise Exception(f"All models failed. Last error: {last_error}")

def process_single_url(product, HD_API):
    api = ViatorAPI()
    supplier = api.get_supplier(product["productCode"])
    print("Supplier:", supplier)
    company_id = HD_API.get_place_id(supplier)
    reviews = HD_API.get_reviews(company_id['placeId'])

    first_review = reviews[0]['snippet']
    first_rating = reviews[0]['rating']
    crowd_score = get_crowd_score_tool(
        review_text=first_review,
        rating=first_rating
    )

    return {
        "company_name": supplier,
        "reviews": first_review,
        "rating": first_rating,
        "crowd_score": crowd_score,
    }

async def process_single_url_async(product, HD_API):
    return await asyncio.to_thread(process_single_url, product, HD_API)

async def process_all_urls(products, HD_API):
    tasks = [process_single_url_async(product, HD_API) for product in products]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results


def run_model(destination_name, start_date, end_date):
    load_dotenv()
    HD_API = HasDataAPI()
    
    # destination_name = input("Enter the destination name: ")
    
    prompt = f"""
    Take the user input and change it into a city or country name. If there was a typo, correct it into the most likely city or country. 
    Dates should also be changed into a format of YYYY-MM-DD.
    Then, use the get_tour_info tool to find tours for that destination. 
    
    For example:
    Austin, Texas -> Austin
    New Yrok -> New York
    Lnddon, UK -> London
    
    Output the resulting list of JSON objects, from the get_tour_info tool for the destination as a list for python, but remove the characters from the url starting at "?mcid" and after.
    Destination: {destination_name}
    Start Date: {start_date}
    End Date: {end_date}
    """

    products = run_with_fallback(prompt)
    
    results = asyncio.run(process_all_urls(products, HD_API))
    
    num = 1
    for result in results:
        if isinstance(result, Exception):
            print(f"Error: {result}")
        else:
            print(f"Result {num}:")
            print(f"Company Name: {result['company_name']}")
            print(f"Review: {result['reviews']}")
            print(f"Rating: {result['rating']}")
            print(f"Crowd Score: {result['crowd_score']}")
        print("-" * 40)
        num += 1

    tour_prompt = f"""
    Given the tour information, determine if it is a "tourist trap" based on the value score. Use the crowd score tool to get the crowd score of 
    every review, obtain the average, and use that to determine the value score by using the get_value_score tool with the price and average
    crowd score as prompts.

    For example:
    Value Score: 4 -> Not a tourist trap
    Value Score: 3 -> Likely not a tourist trap, but expensive
    Value Score: 2 -> Not a tourist trap, but not the greatest experience
    Value Score: 1 -> Very likely a tourist trap
    """
    print(run_with_fallback(tour_prompt))


if __name__ == "__main__":
    run_model("Paris", "2026-10-01", "2026-10-15")