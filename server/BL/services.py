from AL.schemas import BookRatingModel
import psycopg2

import numpy as np
import pandas as pd


class BookService:

    def __init__(self):
        self.db_connection_string = "postgresql://admin:admin@localhost/book_db"  # TODO this really should not be here :) probably should be implemented as a dependency or at least put in a config file

    def calculate_positives(
        self, book_name: str, count: int = 15
    ) -> list[BookRatingModel]:
        result = self._run_recommendation_algorithm(book_name, count)
        print(result)

        return result

    def calculate_negatives(
        self, book_name: str, count: int = 10
    ) -> list[BookRatingModel]:
        raise NotImplementedError()

    def _run_recommendation_algorithm(
        self,
        book_name: str,
        count: int,
    ):
        book_name = book_name.strip().lower()

        df = self._load_book_ratings()
        df = self._filter_ratings_by_relevant_users(df, book_name)
        df = self._filter_ratings_by_min_count(df, book_name, 8)
        avg = df.loc[:, ["title", "rating"]].groupby(by="title").agg("mean")
        df = self._aggregate_by_user_and_book(df)

        recommendations = self._calculate_recommendations(df, avg, book_name)

        # prepare data for pydantic model BookRatingModel
        return recommendations.head(count).to_dict(orient="records")

    def _load_book_ratings(self) -> pd.DataFrame:
        """Load all explicit book ratings into a dataframe with book id as index. Set title to lowercase to simplify string comparison."""
        query = """SELECT book.id AS book_id, title, user_id, rating
                   FROM book
                   INNER JOIN book_rating ON book.id=book_rating.book_id
                   WHERE rating != 0"""

        with psycopg2.connect(self.db_connection_string) as conn:
            df = pd.read_sql_query(query, conn)

        df = df.set_index("book_id")
        df["title"] = df["title"].str.lower()

        return df

    def _filter_ratings_by_relevant_users(
        self, df: pd.DataFrame, book_name: str
    ) -> pd.DataFrame:
        """Filter only reviews that were made by users who read (reviewed) the input book."""

        reference_book_reviews_df = df[df["title"] == book_name]

        from fastapi import HTTPException

        if len(reference_book_reviews_df) == 0:
            raise HTTPException(status_code=404, detail="Book title not found.")

        relevant_users = reference_book_reviews_df["user_id"].unique()

        candidate_reviews_df = df[df["user_id"].isin(relevant_users)]

        return candidate_reviews_df

    def _filter_ratings_by_min_count(
        self, df: pd.DataFrame, book_name: str, N: int
    ) -> pd.DataFrame:
        """Filter only books that were reviewed at least N times."""

        review_count_df = df.groupby("title").agg("count").reset_index()
        filtered_reviews_df = review_count_df[review_count_df["rating"] >= N]
        relevant_books = filtered_reviews_df["title"].to_list()

        # make sure that the input book is not filtered out of the dataframe
        if book_name not in relevant_books:
            relevant_books.append(book_name)

        result = df[df["title"].isin(relevant_books)]

        return result

    def _aggregate_by_user_and_book(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate the reviews by a combination of book title and user id. If a user reviewed a single book multiple times, take the average value.

        Note
        ----
        Leads to a loss of the original index of the dataframe.
        """
        aggregated_df = df.groupby(["user_id", "title"]).agg("mean")
        aggregated_df = aggregated_df.reset_index()
        return aggregated_df

    def _calculate_recommendations(
        self, df: pd.DataFrame, avg: pd.DataFrame, book_name: str
    ) -> pd.DataFrame:
        """Calculate a dataframe with correlations that determine the most recommended books."""
        candidate_books = df["title"].unique().tolist()
        candidate_books.remove(book_name)

        pivot_table = df.pivot(index="user_id", columns="title", values="rating")

        scores = []

        for candidate_title in candidate_books:
            correlation = pivot_table[book_name].corr(pivot_table[candidate_title])
            avg_rating = avg.loc[candidate_title].item()

            scores.append((candidate_title, avg_rating, correlation))

        recommended_books_df = pd.DataFrame(
            scores, columns=["title", "avg_rating", "correlation_idx"]
        )

        recommended_books_df = recommended_books_df.sort_values(
            by=["correlation_idx"], ascending=False
        )

        return recommended_books_df
