from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import router

app = FastAPI()

current_dir = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")
app.include_router(router)
