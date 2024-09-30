from fastapi import FastAPI
from .central_coordinator import router as coordinator_router

def create_app():
    app = FastAPI()
    app.include_router(coordinator_router, prefix="/decision")
    return app
