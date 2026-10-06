from coloredstrings import *
import asyncio
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def main():
    return {"message": "Hello, world"}
