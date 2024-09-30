from fastapi import APIRouter, WebSocket
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import asyncio
import json
from .memory_module import MemoryModule
from .reinforcement_learning import RLAgent
from .rule_optimizer import RuleOptimizer
from common.config import settings
from common.logger import logger

router = APIRouter()
loop = asyncio.get_event_loop()

# Kafka consumer and producer setup
consumer = AIOKafkaConsumer(
    'fused_data',
    loop=loop,
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    group_id="decision_group"
)
producer = AIOKafkaProducer(loop=loop, bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

memory = MemoryModule()
agent = RLAgent(memory)
rule_optimizer = RuleOptimizer()  # 添加规则优化器

@router.on_event("startup")
async def startup_event():
    await consumer.start()
    await producer.start()
    asyncio.create_task(process_decision())
    logger.info("Central coordinator started.")

@router.on_event("shutdown")
async def shutdown_event():
    await consumer.stop()
    await producer.stop()
    logger.info("Central coordinator stopped.")

async def process_decision():
    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode('utf-8'))

            # 检查是否存在会话ID
            session_id = data.get("session_id")
            if not session_id:
                logger.warning("Missing session ID, skipping.")
                continue

            # 存储到短期记忆
            memory.store_short_term(session_id, data)

            # 存储上下文信息
            context = data.get('environment', {})
            memory.store_context(session_id, context)

            # 从长期记忆加载历史数据
            historical_data = memory.load_long_term(session_id)

            # 获取上下文信息
            context_data = memory.get_context(session_id)

            # 使用规则优化器和强化学习代理进行决策
            rule_based_action = rule_optimizer.apply_rules(data)
            if rule_based_action:
                action = rule_based_action
                logger.info(f"Rule-based decision made: {action}")
            else:
                action = agent.decide_action(
                    current_state=data,
                    historical_data=historical_data,
                    context=context_data
                )
                logger.info(f"Reinforcement learning decision made: {action}")

            # 存储决策到长期记忆
            memory.store_long_term(session_id, {'state': data, 'action': action})

            # 将决策发送给执行层
            await producer.send_and_wait("decision_action", json.dumps({
                "session_id": session_id,
                "action": action
            }).encode('utf-8'))
            logger.info("Decision made and sent: %s", action)
    except Exception as e:
        logger.error("Error in central coordinator: %s", e)

@router.websocket("/feedback")
async def feedback_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Feedback websocket connected.")
    try:
        while True:
            feedback_data = await websocket.receive_text()
            # 处理反馈数据，更新强化学习代理
            agent.handle_feedback(feedback_data)
            logger.info("Received feedback: %s", feedback_data)
    except Exception as e:
        logger.error("Websocket error: %s", e)
    finally:
        await websocket.close()
        logger.info("Feedback websocket disconnected.")
