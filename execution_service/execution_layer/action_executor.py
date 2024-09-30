from fastapi import APIRouter, WebSocket
from aiokafka import AIOKafkaConsumer
import asyncio
import json
from .task_manager import TaskManager
from common.config import settings
from common.logger import logger

router = APIRouter()
loop = asyncio.get_event_loop()
consumer = AIOKafkaConsumer('decision_action', loop=loop, bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS, group_id="execution_group")
task_manager = TaskManager()

@router.on_event("startup")
async def startup_event():
    await consumer.start()
    asyncio.create_task(execute_actions())
    logger.info("Action executor started.")

@router.on_event("shutdown")
async def shutdown_event():
    await consumer.stop()
    logger.info("Action executor stopped.")

async def execute_actions():
    try:
        async for msg in consumer:
            action = json.loads(msg.value.decode('utf-8'))
            # 调用任务管理器执行任务
            await task_manager.execute_task(action)
    except Exception as e:
        logger.error("Error in action executor: %s", e)

@router.websocket("/feedback")
async def feedback_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Feedback websocket connected.")
    try:
        while True:
            data = await websocket.receive_text()
            # 将反馈数据发送到决策层
            # 这里可以使用 Kafka 或其他通信方式
            logger.info("Received feedback: %s", data)
    except Exception as e:
        logger.error("Websocket error: %s", e)
    finally:
        await websocket.close()
        logger.info("Feedback websocket disconnected.")
