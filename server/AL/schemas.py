from pydantic import BaseModel


class BookRatingModel(BaseModel):
    name: str
    rating: float
