from fastapi import APIRouter, UploadFile, File
from common.logger import logger
from common.config import settings
from aiokafka import AIOKafkaProducer
import asyncio
import json
import cv2
import numpy as np
import pytesseract
from PIL import Image
from shared_common.neurons.perception_neuron import PerceptionNeuron

router = APIRouter()
loop = asyncio.get_event_loop()
producer = AIOKafkaProducer(loop=loop, bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

class VisualPerception:
    def __init__(self):
        self.video_handler = VideoHandler()
        self.image_handler = ImageHandler()

    async def process_input(self, file: UploadFile):
        contents = await file.read()
        file_extension = file.filename.split('.')[-1].lower()

        if file_extension in ['jpg', 'jpeg', 'png', 'bmp']:
            logger.info(f"Processing image: {file.filename}")
            result = self.image_handler.extract_waybill_number(contents)
            if result:
                signal = PerceptionNeuron(
                    session_id="unique_session_id",
                    dendrite_input={"waybill_number": waybill_number},
                    extracted_information=waybill_number
                )
                await self.send_signal_to_decision_layer(signal)
            else:
                await self.ask_user_help("未能识别出运单号，请提供更多信息。")
        elif file_extension in ['mp4', 'avi', 'mov']:
            logger.info(f"Processing video: {file.filename}")
            results = self.video_handler.process_video(contents)
            await self.send_result(results)
        else:
            logger.error(f"Unsupported file type: {file_extension}")
            await self.ask_user_help("文件类型不支持，请提供图像或视频文件。")

    async def send_signal_to_decision_layer(self, result):
        await producer.send_and_wait(settings.TOPIC_PERCEPTION_TO_DECISION, signal.to_json().encode('utf-8'))
        logger.info("Signal sent to decision layer.")

    async def ask_user_help(self, message):
        await producer.send_and_wait(settings.TOPIC_USER_HELP_REQUESTS, json.dumps({"error": message}).encode('utf-8'))
        logger.info("User help requested.")

# 视频处理逻辑
class VideoHandler:
    def process_video(self, np_input):
        # 视频处理逻辑
        cap = cv2.VideoCapture(np_input)
        results = []
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                results.append(self.process_frame(frame))
            else:
                break
        cap.release()
        return results

    def process_frame(self, frame):
        # 处理每一帧
        avg_color_per_row = np.average(frame, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        return {'average_color': avg_color.tolist()}

# 图像处理逻辑
class ImageHandler:
    def process_image(self, np_input):
        img = cv2.imdecode(np_input, cv2.IMREAD_COLOR)
        if img is not None:
            height, width, _ = img.shape
            return {'height': height, 'width': width}
        else:
            return {'error': 'Failed to process image'}
    
    def extract_waybill_number(file_contents):
        # 使用 OCR 提取运单号
        # 将文件内容解码为 OpenCV 图像
        np_input = np.frombuffer(file_contents, np.uint8)
        img = cv2.imdecode(np_input, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("无法解码输入图像")

        # 使用 OCR 提取文本内容（包括运单号）
        extracted_text = self._extract_text_from_image(img)

        # 使用正则表达式从提取的文本中找到运单号
        waybill_number = self._extract_waybill_from_text(extracted_text)

        return waybill_number
    def _extract_text_from_image(self, img):
        # 使用 pytesseract 提取图像中的文本
        text = pytesseract.image_to_string(img)
        return text

    def _extract_waybill_from_text(self, text):
        import re
        # 假设运单号的格式为字母和数字的组合，例如：ABC123456789
        pattern = r'[A-Z]{3}\d{9}'
        match = re.search(pattern, text)
        if match:
            return match.group(0)
        return None

@router.post("/upload")
async def upload_visual(file: UploadFile = File(...)):
    visual_perception = VisualPerception()
    await visual_perception.process_input(file)
    return {"status": "Visual input received and processed"}
