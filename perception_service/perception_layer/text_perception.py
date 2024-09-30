from fastapi import APIRouter, Request
from common.logger import logger
from common.config import settings
from aiokafka import AIOKafkaProducer
import asyncio
import json

router = APIRouter()
loop = asyncio.get_event_loop()
producer = AIOKafkaProducer(loop=loop, bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

@router.on_event("startup")
async def startup_event():
    await producer.start()
    logger.info("Kafka producer for text perception started.")

@router.on_event("shutdown")
async def shutdown_event():
    await producer.stop()
    logger.info("Kafka producer for text perception stopped.")

@router.post("/input")
async def text_input(request: Request):
    data = await request.json()
    await producer.send_and_wait("text_data", json.dumps(data).encode('utf-8'))
    logger.info("Text data received and sent: %s", data)
    return {"status": "Text data received"}
