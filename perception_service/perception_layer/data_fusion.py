from fastapi import APIRouter
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
from common.config import settings
from common.logger import logger

router = APIRouter()
loop = asyncio.get_event_loop()

# Kafka 消费者
visual_consumer = AIOKafkaConsumer(
    'visual_data',
    loop=loop,
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    group_id="fusion_group"
)
auditory_consumer = AIOKafkaConsumer(
    'auditory_data',
    loop=loop,
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    group_id="fusion_group"
)
text_consumer = AIOKafkaConsumer(
    'text_data',
    loop=loop,
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    group_id="fusion_group"
)
environment_consumer = AIOKafkaConsumer(
    'environment_data',
    loop=loop,
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    group_id="fusion_group"
)

# Kafka 生产者
producer = AIOKafkaProducer(loop=loop, bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

@router.on_event("startup")
async def startup_event():
    await producer.start()
    await visual_consumer.start()
    await auditory_consumer.start()
    await text_consumer.start()
    await environment_consumer.start()
    asyncio.create_task(fuse_data())
    logger.info("Data fusion started.")

@router.on_event("shutdown")
async def shutdown_event():
    await producer.stop()
    await visual_consumer.stop()
    await auditory_consumer.stop()
    await text_consumer.stop()
    await environment_consumer.stop()
    logger.info("Data fusion stopped.")

async def fuse_data():
    try:
        while True:
            visual_msg = await visual_consumer.getone()
            auditory_msg = await auditory_consumer.getone()
            text_msg = await text_consumer.getone()
            environment_msg = await environment_consumer.getone()

            visual_data = json.loads(visual_msg.value.decode('utf-8'))
            auditory_data = json.loads(auditory_msg.value.decode('utf-8'))
            text_data = json.loads(text_msg.value.decode('utf-8'))
            environment_data = json.loads(environment_msg.value.decode('utf-8'))

            # 数据融合
            fused_data = {
                'visual': visual_data,
                'auditory': auditory_data,
                'text': text_data,
                'environment': environment_data
            }

            await producer.send_and_wait("fused_data", json.dumps(fused_data).encode('utf-8'))
            logger.info("Fused data sent.")
    except Exception as e:
        logger.error("Error in data fusion: %s", e)
