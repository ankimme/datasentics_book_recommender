from AL.schemas import BookRatingModel
import psycopg2

import numpy as np
import pandas as pd


class BookService:

    def __init__(self):
        self.db_connection_string = "postgresql://admin:admin@localhost/book_db"  # TODO this really should not be here :)

    def calculate_positives(
        self, book_name: str, count: int = 10
    ) -> list[BookRatingModel]:

        query = """SELECT *
                   FROM book
                   INNER JOIN book_rating ON book.id=book_rating.book_id
                   WHERE rating != 0"""

        # Retrieve data and load it into a DataFrame
        with psycopg2.connect(self.db_connection_string) as conn:
            df = pd.read_sql_query(query, conn)

        result = self._run_algorithm(df, book_name)

        return result

    def calculate_negatives(
        self, book_name: str, count: int = 10
    ) -> list[BookRatingModel]:
        raise NotImplementedError()

    def _run_algorithm(
        self,
        df: pd.DataFrame,
        book_name: str,
    ):
        # TODO this is still ugly and hardcoded
        dataset_lowercase = df.apply(
            lambda x: x.str.lower() if (x.dtype == "object") else x
        )
        tolkien_readers = dataset_lowercase["user_id"][
            (
                dataset_lowercase["title"]
                == "the fellowship of the ring (the lord of the rings, part 1)"
            )
            & (dataset_lowercase["author"].str.contains("tolkien"))
        ]
        tolkien_readers = tolkien_readers.tolist()
        tolkien_readers = np.unique(tolkien_readers)

        # final dataset
        books_of_tolkien_readers = dataset_lowercase[
            (dataset_lowercase["user_id"].isin(tolkien_readers))
        ]

        # Number of ratings per other books in dataset
        number_of_rating_per_book = (
            books_of_tolkien_readers.groupby(["title"]).agg("count").reset_index()
        )

        # select only books which have actually higher number of ratings than threshold
        books_to_compare = number_of_rating_per_book["title"][
            number_of_rating_per_book["user_id"] >= 8
        ]
        books_to_compare = books_to_compare.tolist()

        ratings_data_raw = books_of_tolkien_readers[["user_id", "rating", "title"]][
            books_of_tolkien_readers["title"].isin(books_to_compare)
        ]

        # group by User and Book and compute mean
        ratings_data_raw_nodup = ratings_data_raw.groupby(["user_id", "title"])[
            "rating"
        ].mean()

        # reset index to see User-ID in every row
        ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()

        dataset_for_corr = ratings_data_raw_nodup.pivot(
            index="user_id", columns="title", values="rating"
        )

        LoR_list = ["the fellowship of the ring (the lord of the rings, part 1)"]

        result_list = []
        worst_list = []

        # for each of the trilogy book compute:
        for LoR_book in LoR_list:

            # Take out the Lord of the Rings selected book from correlation dataframe
            dataset_of_other_books = dataset_for_corr.copy(deep=True)
            dataset_of_other_books.drop([LoR_book], axis=1, inplace=True)

            # empty lists
            book_titles = []
            correlations = []
            avgrating = []

            # corr computation
            for book_title in list(dataset_of_other_books.columns.values):
                book_titles.append(book_title)
                correlations.append(
                    dataset_for_corr[LoR_book].corr(dataset_of_other_books[book_title])
                )
                tab = (
                    ratings_data_raw[ratings_data_raw["title"] == book_title]
                    .groupby(ratings_data_raw["title"])["rating"]
                    .mean()
                )
                avgrating.append(tab.min())
            # final dataframe of all correlation of each book
            corr_fellowship = pd.DataFrame(
                list(zip(book_titles, correlations, avgrating)),
                columns=["book", "corr", "avg_rating"],
            )
            corr_fellowship.head()

            a = []
            for _, row in (
                corr_fellowship.sort_values("corr", ascending=False).head(10).iterrows()
            ):
                a.append(
                    BookRatingModel(name=str(row.book), rating=float(row.avg_rating))
                )

            return a
