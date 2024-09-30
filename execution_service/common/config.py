from shared_common.common_config import common_settings

class Settings(common_settings.__class__):
    # 添加该微服务的特定配置
    DECISION_SERVICE_HOST: str = 'decision_service'

settings = Settings()