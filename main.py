from coloredstrings import *
import asyncio
from fastapi import FastAPI, HTTPException, status, Body, Query
from rich.traceback import install

install(show_locals=True)

app = FastAPI()


database = [
    {"author": "Толстой Л.", "text": "Война и Мир"},
    {"author": "Пушкин А.", "text": "Золотая рыбка"},
    {"author": "Гоголь Н", "text": "Вий"},
]


@app.get("/database")
def main():
    return database


