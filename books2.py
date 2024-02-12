from typing import Optional

from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


# Using the pydantic basemodel class to validate
class BookRequest(BaseModel):
    id: Optional[int] = None, Field(title='id is not needed')  # to make the id optional to pass from the user
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    # used to configure the swagger for more detailed descriptions and examples

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'Book of Python',
                'author': 'Roby',
                'description': 'New Description',
                'rating': '4',
                'published_date': '2012'
            }
        }


BOOKS = [
    Book(1, 'Computer Science Pro', 'Amit Singh', 'Nice book', 5, 2010),
    Book(2, 'Math with fun', 'Pratham Sr', 'Nice book and concise points', 4, 2009),
    Book(3, 'Web dev unleashed', 'Alex Johnson', 'Good book', 4, 2009),
    Book(4, 'AI and ML terrors', 'Emily White', 'Average book', 3, 2000),
    Book(5, 'Maths for coders', 'David Brown', 'Not recommended', 1, 2000),
    Book(6, 'Creative writing techniques', 'Ankit Singh', 'Overall Nice book', 2, 2009)]


@app.get("/books", status_code=status.HTTP_200_OK)  # explicit status_code=status.HTTP_200_OK, this line will run after the read_all_books() will run successfully
async def read_all_books():
    return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_one_books(book_id: int = Path(gt=0)):  # Path() we use this to protect the limit in query parameter
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='Item not found')  # raising http exception 404 on not founding the data


# filtering the books according to rating
@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_books_by_rating(book_rating: int = Query(gt=-1, lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return


# filtering by published date
@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_books_by_published_date(book_published_date: int = Query(gt=1999, lt=2031)):  # Query() we use this to protect the limit in query parameter
    books_to_return = []
    for book in BOOKS:
        if book.published_date == book_published_date:
            books_to_return.append(book)
    return books_to_return


# BookRequest class to validate the data coming from post
@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    # As here the type of book_request is of BookRequest class, but we
    # want to convert it to Book class, so we will use the following syntax
    # new_book =Book(**book_request.dict() or **book_request.model_dump())
    # above line is generally providing all the arguments of Book in dictionary form

    new_book = Book(**book_request.dict())
    BOOKS.append(find_book_id(new_book))


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1  # to generate the id automatically
    return book


# Update books using the id

@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')


# Deleting book using id
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')
