from coloredstrings import *
import asyncio
from fastapi import FastAPI, HTTPException, status, Body, Query, Path
from typing import Annotated
from pydantic import BaseModel, Field
from rich.traceback import install

install(show_locals=True)


books = [
    {
        "id": 1,
        "title": "Изучаем Python",
        "author": "Иванов Иван Иванович",
        "year": 2020,
    },
    {
        "id": 2,
        "title": "Основы веб-программирования",
        "author": "Петров Пётр Петрович",
        "year": 2022,
    },
    {
        "id": 3,
        "title": "Алгоритмы для начинающих",
        "author": "Сидорова Анна Сергеевна",
        "year": 2020,
    },
]


app = FastAPI()


@app.get("/books/{id}")
def get_id_books(
    id: Annotated[int, Path(gt=0, description="Введите ID книги")],
) -> dict:

    for book in books:
        if book["id"] == id:
            return book

    raise HTTPException(status.HTTP_404_NOT_FOUND)


@app.get("/books")
def get_year_book(
    year: Annotated[int | None, Query(gt=0, description="Введите год книги")] = None,
) -> list:

    if year is None:
        return books

    cash_boocs = []

    for book in books:
        if book["year"] == year:
            cash_boocs.append(book)
    return cash_boocs


@app.post("/books", status_code=status.HTTP_201_CREATED)
def add_new_book(
    title: Annotated[str, Body(description="Введите название книги")],
    author: Annotated[str, Body(description="Введите автора книги")],
    year: Annotated[int, Body(gt=0, description="Введите год книги")],
) -> dict:

    if not title.strip():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT)

    if not author.strip():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT)

    new_id = max((book["id"] for book in books), default=0) + 1

    new_book = {"id": new_id, "title": title, "author": author, "year": year}

    books.append(new_book)

    return new_book


@app.put("/books/{id}")
def put_book(
    id: Annotated[int, Path(gt=0)],
    title: Annotated[str, Body()],
    author: Annotated[str, Body()],
    year: Annotated[int, Body(gt=0)],
) -> dict:

    if not title.strip():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT)

    if not author.strip():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT)

    for book in books:
        if book["id"] == id:
            book["title"] = title
            book["author"] = author
            book["year"] = year

            return book

    raise HTTPException(status.HTTP_404_NOT_FOUND)


@app.delete("/books/{id}")
def delete_obgect(id: Annotated[int, Path(gt=0)]) -> dict:

    target_book = next((book for book in books if book["id"] == id), None)

    if target_book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    books.remove(target_book)

    return target_book
