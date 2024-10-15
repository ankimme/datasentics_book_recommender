CREATE TABLE book (
    id INT SERIAL PRIMARY KEY,
    isbn TEXT,
    title TEXT,
    author TEXT,
    publication_year INT,
    publisher TEXT, 
    image_url_s TEXT,
    image_url_m TEXT,
    image_url_l TEXT
);

CREATE TABLE book_rating (
    id INT SERIAL PRIMARY KEY,
    user_id INT,
    book_id INT NOT NULL,
    rating FLOAT,
    CONSTRAINT fk_isbn
    FOREIGN KEY(book_id)
    REFERENCES book(id)
);


CREATE INDEX book_isbn_index
ON book(isbn);