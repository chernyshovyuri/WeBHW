from coloredstrings import *
import asyncio
from fastapi import FastAPI, HTTPException, status, Body, Query
from typing import Annotated
from rich.traceback import install

install(show_locals=True)


app = FastAPI()

