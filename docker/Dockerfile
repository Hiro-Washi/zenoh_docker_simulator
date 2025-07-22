# Base image with Python
# シミュレーションの各ノード（アプリケーション）コンテナのベースとなるイメージ
# Pythonアプリケーションを実行できる基本的な環境を構築する
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies that might be required by Python packages
# (e.g., for building native extensions)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# Copy the application source code into the container
# The 'apps' directory will be mounted at runtime, but we copy it here
# to ensure dependencies can be installed during the build process.
COPY ./apps /app/apps

# Copy the requirements file for the specific app
# This will be specified as a build argument.
ARG APP_NAME
COPY ./apps/${APP_NAME}/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# The command to run the application will be specified in docker-compose.yaml
# For example: CMD ["python", "apps/sample_publisher/main.py"]
