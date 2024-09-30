from fastapi import FastAPI
from .learning_optimizer import router as optimizer_router

def create_app():
    app = FastAPI()
    app.include_router(optimizer_router, prefix="/feedback")
    return app
