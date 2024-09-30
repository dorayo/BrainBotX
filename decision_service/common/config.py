from shared_common.common_config import common_settings

class Settings(common_settings.__class__):
    # 添加该微服务的特定配置
    FOO: str = 'bar'

settings = Settings()
