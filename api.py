from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date

from AI import run_model
from tools import get_crowd_score_tool

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

class TourResponse(BaseModel):
	tour_name: str
	score: int
	price: int
	locations: list[dict[str, str]]
	viator_link: str



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
    Returns the top tour URL, company name, reviews, and crowd score.
    """

    # sample_response = {
    #     "tour_name": "New York Sample Tour",
    #     "score": 4,
    #     "price": 6767,
    #     "locations": [{"name": "Sample Location 1"}, {"name": "Sample Location 2"}],
    #     "viator_link": "www.viator.com"
    # }

    # return sample_response

    try:
        result = run_model(body.destination, str(body.start_date), str(body.end_date))
        return TourResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
