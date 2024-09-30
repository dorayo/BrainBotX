from datetime import datetime, timedelta
from common.logger import logger
from common.config import settings
from shared_common.neurons.decision_neuron import DecisionNeuron
from shared_common.neurons.perception_neuron import PerceptionNeuron
import re
import redis

class RuleOptimizer:
    def __init__(self):
        self.waybill_pattern = r'[A-Z]{2}\d{9,12}'  # 运单号正则表达式
        self.redis_client = self.get_redis_client()  # 获取 Redis 客户端

    def get_redis_client(self):
        # 初始化 Redis 客户端，用于查询用户的历史信息等
        return redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

    def apply_rules(self, signal: PerceptionNeuron) -> DecisionNeuron:
        """
        根据输入神经元的感知数据应用规则，生成决策神经元
        """
        logger.info("Applying rule-based decision logic.")
        
        # 获取感知神经元中的数据
        session_id = signal.session_id
        waybill_number = signal.extracted_information.get('waybill_number')
        user_phone = signal.dendrite_input.get('user_phone')
        delivery_time = signal.dendrite_input.get('delivery_time')  # 假设有快递投递时间
        
        # 1. 验证是否提供了有效的运单号
        if not waybill_number or not self.is_valid_waybill(waybill_number):
            logger.warning("Invalid or missing waybill number.")
            return DecisionNeuron(
                session_id=session_id,
                dendrite_input=signal.dendrite_input,
                action="request_more_info",
                context="Please provide a valid waybill number."
            )

        # 2. 检查该运单号的快递状态
        locker_info = self.query_locker_status(waybill_number)
        if not locker_info:
            logger.warning(f"Waybill number {waybill_number} not found in system.")
            return DecisionNeuron(
                session_id=session_id,
                dendrite_input=signal.dendrite_input,
                action="not_in_locker",
                context=f"The waybill number {waybill_number} is not associated with any locker."
            )

        # 3. 查询用户是否最近有取件记录
        if self.user_has_recent_activity(user_phone, locker_info['locker_location']):
            # 如果用户最近取过件，可以直接告知取件码和快递位置
            return DecisionNeuron(
                session_id=session_id,
                dendrite_input=signal.dendrite_input,
                action="provide_pickup_info",
                context={
                    "waybill_number": waybill_number,
                    "pickup_code": locker_info['pickup_code'],
                    "locker_location": locker_info['locker_location'],
                    "delivery_time": delivery_time
                }
            )

        # 4. 检查是否超期且用户未收到通知
        if self.is_package_overdue(delivery_time) and not self.sms_notification_accurate(user_phone):
            return DecisionNeuron(
                session_id=session_id,
                dendrite_input=signal.dendrite_input,
                action="confirm_phone_number",
                context="Your package is overdue, but we noticed a discrepancy with the phone number. Please confirm your number."
            )

        # 5. 超期并发送短信提醒
        if self.is_package_overdue(delivery_time):
            return DecisionNeuron(
                session_id=session_id,
                dendrite_input=signal.dendrite_input,
                action="request_overdue_payment",
                context=f"Your package with waybill {waybill_number} is overdue. Please pay the overdue fees to retrieve your package."
            )

        # 默认返回无匹配的情况
        return DecisionNeuron(
            session_id=session_id,
            dendrite_input=signal.dendrite_input,
            action="no_action_required",
            context="No further action needed."
        )

    def is_valid_waybill(self, waybill_number):
        """
        判断是否为有效的运单号
        """
        return bool(re.match(self.waybill_pattern, waybill_number))

    def query_locker_status(self, waybill_number):
        """
        查询运单号对应的快递柜信息
        """
        # 示例查询，实际应从数据库或缓存中获取信息
        locker_data = {
            "locker_location": "Block A, Apartment 12",
            "pickup_code": "123456",
            "delivery_time": "2024-09-25 10:30:00"
        }
        return locker_data

    def user_has_recent_activity(self, user_phone, locker_location):
        """
        判断用户在某个快递柜位置是否有最近取件记录
        """
        recent_activity = self.redis_client.get(f"user:{user_phone}:activity")
        if recent_activity:
            activity_data = recent_activity.decode('utf-8')
            return activity_data == locker_location  # 示例逻辑
        return False

    def is_package_overdue(self, delivery_time):
        """
        判断包裹是否已经超期
        """
        delivery_datetime = datetime.strptime(delivery_time, '%Y-%m-%d %H:%M:%S')
        overdue_threshold = delivery_datetime + timedelta(days=3)  # 3天为超期标准
        return datetime.utcnow() > overdue_threshold

    def sms_notification_accurate(self, user_phone):
        """
        判断是否发送过准确的取件短信通知
        """
        sms_record = self.redis_client.get(f"user:{user_phone}:sms")
        if sms_record:
            return True
        return False
