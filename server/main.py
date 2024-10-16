from AL.schemas import BookRatingModel
from BL.services import BookService

from typing import Annotated
from fastapi import Depends

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# TODO do not use this wildcard in production
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Name": "Book recommender", "Version": "1.0", "Author": "Andrea Chimenti"}


@app.get("/positives/{book_name}")
def get_positives(
    service: Annotated[BookService, Depends()], book_name: str
) -> list[BookRatingModel]:
    return service.calculate_positives(book_name)


@app.get("/negatives/{book_name}")
def get_negatives(
    service: Annotated[BookService, Depends()], book_name: str
) -> list[BookRatingModel]:
    # TODO
    return []
