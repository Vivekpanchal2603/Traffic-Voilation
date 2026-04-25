from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import upload, process

app = FastAPI(
    title="Traffic AI Backend",
    version="1.0.0"
)

app.include_router(upload.router)
app.include_router(process.router)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")