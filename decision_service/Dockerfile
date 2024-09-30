FROM python:3.9-slim

# 设置工作目录为 /app
WORKDIR /app

# 替换源并清空 /etc/apt/sources.list.d 内容
RUN rm -rf /etc/apt/sources.list.d/* && \
    echo "deb http://mirrors.aliyun.com/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian-security bookworm-security main" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian bookworm-updates main" >> /etc/apt/sources.list && \
    apt-get clean && apt-get update && \
    apt-get install -y build-essential --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# 复制 shared_common 文件夹到 /app/decision_service/shared_common
COPY ./shared_common /app/decision_service/shared_common

# 复制 decision_service 文件夹到 /app/decision_service
COPY ./decision_service /app/decision_service

# 设置 PYTHONPATH 确保 shared_common 可被引用
ENV PYTHONPATH=/app

# 切换工作目录到 /app/decision_service
WORKDIR /app/decision_service

# 复制 requirements.txt 并安装依赖
COPY ./decision_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

# 暴露端口 8002
EXPOSE 8002

# 运行应用
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
