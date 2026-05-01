from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import app.api.routes.upload as upload
import app.api.routes.process as process
import app.api.routes.dashboard as dashboard

app = FastAPI(
    title="Traffic AI Backend",
    version="1.0.0"
)

# API ROUTES FIRST
app.include_router(upload.router)
app.include_router(process.router)
app.include_router(dashboard.router)

# STATIC FILES AFTER ROUTES
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")