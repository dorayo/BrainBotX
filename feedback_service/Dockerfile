# 使用 Python 3.9 作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 替换源并清空 /etc/apt/sources.list.d 内容
RUN rm -rf /etc/apt/sources.list.d/* && \
    echo "deb http://mirrors.aliyun.com/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian-security bookworm-security main" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian bookworm-updates main" >> /etc/apt/sources.list && \
    apt-get clean && apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制 shared_common 文件夹，以便跨微服务共享通用逻辑
COPY ./shared_common /app/feedback_service/shared_common

# 复制 feedback_service 代码
COPY ./feedback_service /app/feedback_service

# 设置 PYTHONPATH 确保 shared_common 可被引用
ENV PYTHONPATH=/app

# 切换工作目录到 feedback_service
WORKDIR /app/feedback_service

# 复制 requirements.txt 并安装依赖
COPY ./feedback_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

# 暴露服务的端口
EXPOSE 8004

# 启动命令，运行 FastAPI 应用
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8004"]