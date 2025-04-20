# 使用官方 Python 镜像
FROM python:3.9.21

# 设置工作目录
WORKDIR /app

# 复制文件到容器中
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量，防止 Python 缓存
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 启动 Flask 应用（注意：确保 app.py 中有 app 对象）
CMD ["python", "app.py"]
