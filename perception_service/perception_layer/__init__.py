from fastapi import FastAPI
from .visual_perception import router as visual_router
from .auditory_perception import router as auditory_router
from .text_perception import router as text_router
from .environment_perception import router as environment_router
from .data_fusion import router as fusion_router

def create_app():
    app = FastAPI()
    app.include_router(visual_router, prefix="/visual")
    app.include_router(auditory_router, prefix="/auditory")
    app.include_router(text_router, prefix="/text")
    app.include_router(environment_router, prefix="/environment")
    app.include_router(fusion_router, prefix="/fusion")
    return app
