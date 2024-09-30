import mysql.connector
from common.config import settings
from common.logger import logger

def get_long_term_memory():
    conn = mysql.connector.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DB
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT state, action FROM long_term_memory")
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    logger.info("Retrieved long-term memory records.")
    return records
