from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from services import user_router



app=FastAPI()
templates_dir="./templates"
app.include_router(user_router,prefix="/user")
app.mount("/static",StaticFiles(directory="./styles"),name="styles")


