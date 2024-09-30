# feedback_service/feedback_layer/learning_optimizer.py

from fastapi import APIRouter
from common.logger import logger
from .models import get_long_term_memory


router = APIRouter()
# agent = RLAgent(memory=None)  # 这里的 memory 可以是空，因为我们只需要更新模型

@router.get("/optimize")
def optimize():
    try:
        experiences = get_long_term_memory()
        for exp in experiences:
            state = json.loads(exp['state'])
            action = exp['action']
            # 假设有 reward 字段，或者根据执行结果计算 reward
            reward = compute_reward(state, action)
            # agent.update_model(state, action, reward)
        logger.info("Model updated based on long-term memory.")
        return {"status": "Optimization completed"}
    except Exception as e:
        logger.error("Error in optimization: %s", e)
        return {"status": "Error", "message": str(e)}

def compute_reward(state, action):
    # 根据业务逻辑计算奖励值
    # 示例：如果动作成功，则奖励为1，否则为0
    return 1  # 需要根据实际情况实现
