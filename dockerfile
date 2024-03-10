# 使用官方 Python 运行时作为父镜像
FROM python:3.9-slim

# 设置工作目录为 /app
WORKDIR /app

# 将当前目录内容复制到位于 /app 的容器中
COPY . /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1

RUN pip3 install --upgrade pip

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

# 在容器启动时先运行 main.py，然后运行 server.py
CMD ["sh", "-c", "python3 main.py && python3 server.py"]
