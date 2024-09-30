from fastapi import APIRouter, UploadFile, File
import whisper
import os
import asyncio
import json
import logging
from aiokafka import AIOKafkaProducer
# import speech_recognition as sr

router = APIRouter()
logger = logging.getLogger(__name__)

# 加载 Whisper 模型（可以选择不同大小的模型: tiny, base, small, medium, large）
model = whisper.load_model("base")

# Kafka 生产者配置
producer = AIOKafkaProducer(
    bootstrap_servers='kafka:9092',  # 确保这里的地址正确
)

# mic = sr.Microphone()  # 使用语音识别的麦克风

@router.on_event("startup")
async def startup_event():
    await producer.start()
    logger.info("Kafka producer for auditory perception started.")
    asyncio.create_task(capture_audio())  # 启动音频捕获任务

@router.on_event("shutdown")
async def shutdown_event():
    await producer.stop()
    logger.info("Kafka producer for auditory perception stopped.")

async def capture_audio():
    # recognizer = sr.Recognizer()
    # with mic as source:
    #     recognizer.adjust_for_ambient_noise(source)
    # while True:
    #     with mic as source:
    #         audio = recognizer.listen(source, phrase_time_limit=5)
    #     try:
    #         # 将捕获的音频转换为 WAV 格式并保存为临时文件
    #         temp_file_path = "temp_audio.wav"
    #         with open(temp_file_path, "wb") as f:
    #             f.write(audio.get_wav_data())

    #         # 使用 Whisper 模型进行转录
    #         result = model.transcribe(temp_file_path)
    #         text = result['text']
    #         auditory_data = {'text': text}

    #         await producer.send_and_wait("auditory_data", json.dumps(auditory_data).encode('utf-8'))
    #         logger.info("Auditory data sent from capture: %s", text)
    #         os.remove(temp_file_path)  # 删除临时文件
    #     except Exception as e:
    #         logger.error("Error in audio processing: %s", str(e))
    #     await asyncio.sleep(0.1)
    pass

@router.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    # 确保接收到的文件类型为音频文件
    if not file.content_type.startswith("audio/"):
        return {"error": "File type not supported."}

    # 将上传的音频文件保存到临时文件
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as f:
        f.write(await file.read())

    # 使用 Whisper 模型进行转录
    result = model.transcribe(temp_file_path)

    # 删除临时文件
    os.remove(temp_file_path)

    # 将转录文本发送到 Kafka
    auditory_data = {'text': result['text']}
    await producer.send_and_wait("auditory_data", json.dumps(auditory_data).encode('utf-8'))
    logger.info("Auditory data sent from upload: %s", result['text'])

    return {"transcription": result['text']}
