# execution_service/execution_layer/real_time_feedback.py

import asyncio
from common.logger import logger
import websockets
from common.config import settings
import json

class RealTimeFeedback:
    def __init__(self):
        self.websocket_uri = f"ws://{settings.DECISION_SERVICE_HOST}:8002/decision/feedback"

    async def send_feedback(self, feedback_data):
        try:
            async with websockets.connect(self.websocket_uri) as websocket:
                await websocket.send(json.dumps(feedback_data))
                logger.info("Sent feedback: %s", feedback_data)
        except Exception as e:
            logger.error("Failed to send feedback: %s", e)
