import litellm
from smolagents import LiteLLMModel, CodeAgent, InferenceClientModel
from openai import OpenAI
from reviews.hasdata import HasDataAPI
from viator import ViatorAPI
from tools import get_tour_info_tool, get_crowd_score_tool, get_value_score_tool
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
        tools=[get_tour_info_tool, get_crowd_score_tool, get_value_score_tool],
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
    company_id = HD_API.get_place_id(supplier)
    reviews = HD_API.get_reviews(company_id['placeId'])
    
    description = api.get_description(product["productCode"])

    filtered_reviews = [
        {"snippet": review["snippet"], "rating": review["rating"]}
        for review in reviews
    ]
    
    crowd_scores = []
    value_scores = []
    for review in reviews:
        try:
            score = get_crowd_score_tool(
                review_text=review["snippet"],
                rating=review["rating"]
            )
            crowd_scores.append(score)
            
            value = get_value_score_tool(
                price=product.get("price"),
                average_sentiment=score
            )
            value_scores.append(value)
        except Exception as e:
            print(f"Error processing review: {e}")
            continue
    
    value_avg = sum(value_scores) / len(value_scores)
    
    prompt = f"""
    You're a tour review tool that provides an explanation for why a tour has been given a specified score of recommended or not due to it being a tourist trap.
    
    The following is how you can interpret a value score:
    Value Score: 4 -> Not a tourist trap
    Value Score: 3 -> Likely not a tourist trap, but expensive
    Value Score: 2 -> Not a tourist trap, but not the greatest experience
    Value Score: 0-1 -> Very likely a tourist trap
    
    Your response should align with the value score. Based on the reviews, make a short 20-30 word response as to why you would or would not recommend this tour:
    Reviews: {filtered_reviews}
    Average Value Score: {value_avg}
    """
    
    response = run_with_fallback(prompt)
    
    return {
        "company_name": supplier,
        "tour_name": product["title"],
        "score": value_avg,
        "price": product.get("price"),
        "reasoning": response,
        "viator_link": product.get("url"),
        "description": description
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
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Error: {result}")
        else:
            print(f"Result {i+1}:")
            print(f"Company Name: {result['company_name']}")
            print(f"Tour Name: {result['tour_name']}")
            print(f"Pricing: {result.get('price')}")
            print(f"Score: {result.get('score')}")
            print(f"Reasoning: {result.get('reasoning')}")
            print(f"Viator Link: {result.get('viator_link')}")
            print(f"Description: {result.get('description')}")
        print("-" * 40)


if __name__ == "__main__":
    run_model("Paris", "2026-10-01", "2026-10-15")