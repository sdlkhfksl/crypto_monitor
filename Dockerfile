# 使用官方Python镜像
FROM python:3.9-slim

# 创建并设置工作目录
WORKDIR /app

# 复制本地代码到容器中
COPY . /app

# 安装requirements.txt文件中指定的依赖
RUN pip install --no-cache-dir -r requirements.txt

# 指定容器启动时执行的命令
CMD ["python", "./bot.py"]
