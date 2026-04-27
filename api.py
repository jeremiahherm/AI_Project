from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date

from AI import run_model
from tools import get_crowd_score_tool

from database import find_tours_for_destination, save_tours

app = FastAPI(title="Tour Intelligence API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request / Response Models ---

class TourRequest(BaseModel):
    destination: str
    start_date: date
    end_date: date

class Reviews(BaseModel):
    company_name: str
    tour_name: str
    score: float
    price: float
    reasoning: str
    viator_link: str
    description: str
class TourResponse(BaseModel):
    destination: str
    start_date: str
    end_date: str
    reviews: list[Reviews]


class ToursResponse(BaseModel):
	tours: list[TourResponse]



class SentimentRequest(BaseModel):
    review_text: str
    rating: float


# --- Routes ---

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tours")
def request_tours(body: TourRequest):
    """
    Run a tour search for a destination and date range.
    Returns all tours with their details, reviews, and crowd scores.
    """

    try:
        destination = body.destination
        start_date = str(body.start_date)
        end_date = str(body.end_date)

        start_date_formatted = date.fromisoformat(start_date)
        end_date_formatted = date.fromisoformat(end_date)

        if (start_date_formatted >= end_date_formatted):
            raise ValueError("Start date must be before end date.")
            return {"error": "Start date must be before end date."}
        if (start_date_formatted < date.today()):
            raise ValueError("Start date cannot be in the past.")
            return {"error": "Start date cannot be in the past."}
        

        tour = find_tours_for_destination(destination)
        if tour:
            print(f"Found a tour in database")
            return {"tours": tour}
        else:
            print("Could not find tour in database, switching to model....")
            results = run_model(destination, start_date, end_date)

            if not results:
                raise ValueError("No tours found for the given destination and date range.")
                return {"error": "No tours found for the given destination and date range."}

            save_tours(destination, start_date, end_date, results)
            return {"tours": results}        
    except Exception as e:
        return {"error": str(e)}


@app.post("/sentiment")
def analyze_sentiment(body: SentimentRequest):
    """
    Directly analyze the sentiment of a review without running the full agent.
    """

    return {"result": 'This endpoint tests the sentiment analysis tool. Please check back later.'}

    try:
        result = get_crowd_score_tool.forward(body.review_text, body.rating)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
