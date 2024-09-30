import aiohttp
from common.logger import logger

async def call_external_api(api_url, payload, feedback):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload) as response:
                resp_data = await response.json()
                logger.info("Called external API: %s", api_url)
                await feedback.send_feedback(f"API response: {resp_data}")
                return resp_data
    except Exception as e:
        logger.error("Error calling external API: %s", e)
        await feedback.send_feedback(f"Error: {e}")
        return None
