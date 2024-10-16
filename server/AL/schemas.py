from pydantic import BaseModel


class BookRatingModel(BaseModel):
    title: str
    avg_rating: float
    correlation_idx: float
