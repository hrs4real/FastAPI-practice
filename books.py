# To run FastAPI app use uvicorn book:app --reload --port 5000
# To create virtual env for fast api use >> python -m venv {foldername}
# >> install uvicorn[standard] and fastapi


from fastapi import Body, FastAPI

app = FastAPI()

Books = [{"title": "Title one", "author": "Author one", "category": "science"},
         {"title": "Title two", "author": "Author two", "category": "maths"},
         {"title": "Title three", "author": "Author three", "category": "science"},
         {"title": "Title four", "author": "Author two", "category": "history"},
         {"title": "Title five", "author": "Author four", "category": "science"},
         {"title": "Title six", "author": "Author three", "category": "math"}]


@app.get("/books")
async def get_books():
    return Books


# As fast api executes the functions in chronological order we place it above dynamic param
# @app.get("/books/mybook")
# async def get_books():
#     return {'book_title':'My favorite book'}


@app.get("/books/{book_title}")
async def get_books_dynamic_param(book_title: str):
    for book in Books:
        if book.get('title').casefold() == book_title.casefold():
            return book
    return {'title': "Not found"}


@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in Books:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


@app.get("/books/author/")
async def get_books_by_author(book_author: str):
    books_to_return = []
    for book in Books:
        if book.get("author").casefold() == book_author.casefold():
            books_to_return.append(book)
    return books_to_return


@app.get("/books/{book_author}/")
async def read_author_category_by_query(book_author: str, category: str):
    books_to_return = []
    for book in Books:
        if book.get('author').casefold() == book_author.casefold() and \
                book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


# We can send data in body, so we import body for post
# Get method cannot have a body


@app.post("/books/create_book")
async def create_book(new_book=Body()):
    Books.append(new_book)

# Put is Very similar to post request


@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for i in range(len(Books)):
        if Books[i].get("title").casefold() == updated_book.get("title").casefold():
            Books[i] = updated_book


@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(Books)):
        if Books[i].get("title").casefold() == book_title.casefold():
            Books.pop(i)
            break
