# 使用Ubuntu作为基础镜像，PaddlePaddle在Ubuntu上有更好的支持
FROM ubuntu:20.04

# 设置环境变量，避免交互式安装
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 设置PaddlePaddle环境变量
ENV FLAGS_allocator_strategy=auto_growth
ENV FLAGS_fraction_of_gpu_memory_to_use=0.5

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential \
    cmake \
    pkg-config \
    libopencv-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgfortran5 \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    gfortran \
    wget \
    curl \
    git \
    poppler-utils \
    libpoppler-cpp-dev \
    fonts-dejavu-core \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# 创建符号链接，确保python命令可用
RUN ln -s /usr/bin/python3 /usr/bin/python

# 升级pip
RUN python3 -m pip install --upgrade pip setuptools wheel

# 设置工作目录
WORKDIR /app

# 首先复制requirements.txt，利用Docker缓存
COPY requirements.txt /app/

# 安装Python依赖
# 先安装PaddlePaddle CPU版本
RUN pip install paddlepaddle==2.5.2 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装其他依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 创建必要的目录
RUN mkdir -p /app/uploads/temp

# 复制应用代码
COPY ./ /app/

# 设置权限
RUN chmod +x /app/main.py

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# 运行Python程序
CMD ["python", "main.py"]
