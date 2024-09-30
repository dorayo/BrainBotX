# common_config.py
from pydantic import BaseSettings

class CommonSettings(BaseSettings):
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str
    KAFKA_BOOTSTRAP_SERVERS: str
    REDIS_HOST: str
    REDIS_PORT: int

    # Kafka topics
    TOPIC_PERCEPTION_TO_DECISION: str = "perception_to_decision"
    TOPIC_DECISION_TO_EXECUTION: str = "decision_to_execution"
    TOPIC_EXECUTION_TO_FEEDBACK: str = "execution_to_feedback"
    TOPIC_FEEDBACK_TO_DECISION: str = "feedback_to_decision"
    TOPIC_USER_HELP_REQUESTS: str = "user_help_requests"  

    class Config:
        env_file = '../.env'

common_settings = CommonSettings()