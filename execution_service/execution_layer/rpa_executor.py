# execution_service/execution_layer/rpa_executor.py
from common.logger import logger

async def execute_rpa_task(task_details, feedback):
    try:
        if task_details['type'] == 'click':
            logger.info("Executed click at %s", task_details['position'])
            await feedback.send_feedback({'action': 'click', 'position': task_details['position'], 'status': 'success'})
        elif task_details['type'] == 'type':
            logger.info("Typed text: %s", task_details['text'])
            await feedback.send_feedback({'action': 'type', 'text': task_details['text'], 'status': 'success'})
        else:
            logger.warning("Unknown RPA task type: %s", task_details['type'])
            await feedback.send_feedback({'action': task_details['type'], 'status': 'unknown'})
    except Exception as e:
        logger.error("Error in RPA task: %s", e)
        await feedback.send_feedback({'action': task_details.get('type'), 'status': 'error', 'message': str(e)})