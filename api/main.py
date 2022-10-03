
from typing import Union

from fastapi import FastAPI
from api.routes import users


app = FastAPI()

app.include_router(users.router)

@app.get("/")
def read_root():
    return {"msg": "App Works"}
