from smolagents import LiteLLMModel, CodeAgent, InferenceClientModel
from tools import get_tour_info_tool, get_crowd_score_tool
import os
from dotenv import load_dotenv
import time
import requests


def run_model(destination_name, start_date, end_date):
    load_dotenv()
    print("Loaded key:", os.getenv("GEMINI_API_KEY")[:6])
    
    def create_agent(model_id):
        model = LiteLLMModel(
            model_id=model_id,
            api_key=os.getenv("GEMINI_API_KEY"),
            num_retries=3,  # built-in retry
        )

        return CodeAgent(
            tools=[get_tour_info_tool, get_crowd_score_tool],
            model=model
        )


    def run_with_fallback(prompt):
        models = [
            "gemini/gemini-2.5-flash",
            "gemini/gemini-2.5-flash-lite",
        ]

        for model_id in models:
            try:
                print(f"Trying model: {model_id}")
                agent = create_agent(model_id)
                return agent.run(prompt)

            except Exception as e:
                print(f"Failed with {model_id}: {e}")
                time.sleep(2)  # small backoff

        raise Exception("All models failed")

    destination_name = input("Enter the destination name: ")

    prompt = f"""
    Take the user input and change it into a city or country name. If there was a typo, correct it into the most likely city or country. 
    Dates should also be changed into a format of YYYY-MM-DD.
    Then, use the get_tour_info tool to find tours for that destination. 
    
    For example:
    Austin, Texas -> Austin
    New Yrok -> New York
    Lnddon, UK -> London
    
    Output the resulting URLs from the get_tour_info tool for the destination, but remove the characters from the url starting at "?mcid" and after.
    Destination: {destination_name}
    Start Date: {start_date}
    End Date: {end_date}
    """

    result = run_with_fallback(prompt)
    print(result)


if __name__ == "__main__":
    run_model("Paris", "2026-10-01", "2026-10-15")