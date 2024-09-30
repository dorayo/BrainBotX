from fastapi import FastAPI
from .action_executor import router as executor_router

def create_app():
    app = FastAPI()
    app.include_router(executor_router, prefix="/execute")
    return app
