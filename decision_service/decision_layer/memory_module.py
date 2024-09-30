# decision_service/decision_layer/memory_module.py

from common.config import settings
import redis
import mysql.connector
from datetime import datetime
from common.logger import logger
import json

class MemoryModule:
    def __init__(self):
        # 短期记忆使用 Redis
        self.redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        # 长期记忆使用 MySQL
        self.mysql_conn = mysql.connector.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DB
        )
        self.create_tables()

    def create_tables(self):
        cursor = self.mysql_conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS long_term_memory (
            session_id VARCHAR(255) PRIMARY KEY,
            state JSON,
            action JSON,
            timestamp DATETIME
        )
        """)
        self.mysql_conn.commit()
        cursor.close()
        logger.info("Long-term memory table ensured.")

    def store_short_term(self, data):
        # 存储到 Redis，设置过期时间
        self.redis_client.setex(f'{session_id}_short_term', 600, value=json.dumps(data))
        logger.info("Data stored in short-term memory.")

    def load_short_term(self):
        data = self.redis_client.get(f'{session_id}_short_term')
        if data:
            logger.info("Loaded data from short-term memory.")
            return json.loads(data)
        else:
            logger.warning("No data in short-term memory.")
            return None

    def store_long_term(self, data):
        cursor = self.mysql_conn.cursor()
        cursor.execute("""
        INSERT INTO long_term_memory (session_id, state, action, timestamp) VALUES (%s, %s, %s, %s)
        """, (session_id, json.dumps(data['state']), json.dumps(data['action']), datetime.utcnow()))
        self.mysql_conn.commit()
        cursor.close()
        logger.info("Data stored in long-term memory.")

    def load_long_term(self):
        cursor = self.mysql_conn.cursor(dictionary=True)
        cursor.execute("""
        SELECT state, action FROM long_term_memory WHERE session_id = %s ORDER BY timestamp DESC LIMIT 100
        """, (session_id,))
        records = cursor.fetchall()
        cursor.close()
        logger.info("Loaded data from long-term memory.")
        # 返回最近的100条记录
        return records if records else []

    def store_context(self, session_id, context_data):
        self.redis_client.set(f'{session_id}_context', json.dumps(context_data))
        logger.info("Context data stored in memory.")

    def get_context(self, session_id):
        data = self.redis_client.get(f'{session_id}_context')
        logger.info("Context data retrieved from memory.")
        return json.loads(data) if data else {}
