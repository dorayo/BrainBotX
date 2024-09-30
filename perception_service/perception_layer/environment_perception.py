
from fastapi import APIRouter
import asyncio
from common.logger import logger
from common.config import settings
from aiokafka import AIOKafkaProducer
import json
import time

router = APIRouter()
loop = asyncio.get_event_loop()
producer = AIOKafkaProducer(loop=loop, bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

@router.on_event("startup")
async def startup_event():
    await producer.start()
    logger.info("Kafka producer for environment perception started.")
    asyncio.create_task(capture_environment())

@router.on_event("shutdown")
async def shutdown_event():
    await producer.stop()
    logger.info("Kafka producer for environment perception stopped.")

async def capture_environment():
    while True:
        environment_data = get_environment_data()
        await producer.send_and_wait("environment_data", json.dumps(environment_data).encode('utf-8'))
        logger.info("Environment data sent.")
        await asyncio.sleep(5)  # 每5秒采集一次环境信息

def get_environment_data():
    # 示例：获取当前时间和模拟的地理位置
    environment_data = {
        'timestamp': time.time(),
        'location': 'Office',
        'weather': 'Sunny',  # 可以通过API获取真实天气
        'user_status': 'Active'  # 可以根据业务逻辑定义
    }
    return environment_data
