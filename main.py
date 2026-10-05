from coloredstrings import * 

from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
async def hello_world():
    return {"Hello, world"}




