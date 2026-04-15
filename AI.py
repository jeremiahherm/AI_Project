import litellm
from smolagents import LiteLLMModel, CodeAgent, InferenceClientModel
from openai import OpenAI
from tools import get_tour_info_tool, get_crowd_score_tool, search_tool
import os
from dotenv import load_dotenv
import time
import logging
import random
import time
import ast
import requests


def run_model(destination_name, start_date, end_date):
    load_dotenv()
    
    def create_agent(model_id):
        model = LiteLLMModel(
            model_id=model_id,
            api_key=os.getenv("OPENAI_API_KEY"),
            num_retries=3,  # built-in retry
        )

        return CodeAgent(
            tools=[get_tour_info_tool, get_crowd_score_tool, search_tool],
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

    # destination_name = input("Enter the destination name: ")

    prompt = f"""
    Take the user input and change it into a city or country name. If there was a typo, correct it into the most likely city or country. 
    Dates should also be changed into a format of YYYY-MM-DD.
    Then, use the get_tour_info tool to find tours for that destination. 
    
    For example:
    Austin, Texas -> Austin
    New Yrok -> New York
    Lnddon, UK -> London
    
    Output the resulting URLs from the get_tour_info tool for the destination as a list for python, but remove the characters from the url starting at "?mcid" and after.
    Destination: {destination_name}
    Start Date: {start_date}
    End Date: {end_date}
    """

    urls = run_with_fallback(prompt)
    
    # Make this asynch for all links in urls, but for now just do it for the first one
    search_prompt = f"""
    Given the following URL, use the search tool to find the company name of the tour provider.
    The URL provided takes you to the Viator page for the tour, the company name or LLC can be found on that page.
    
    URL: {urls[0]}
    
    Output only the company name or LLC name as a string.
    """
    company_name = run_with_fallback(search_prompt)
    print(f"URLs: {urls[0]}")
    print(f"Company Name: {company_name}")


if __name__ == "__main__":
    run_model("Paris", "2026-10-01", "2026-10-15")