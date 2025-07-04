# 多阶段构建 Dockerfile
FROM node:18-alpine AS frontend-builder

# 设置工作目录
WORKDIR /app/frontend

# 安装pnpm
RUN npm install -g pnpm

# 复制前端依赖文件
COPY frontend/package.json ./
COPY frontend/pnpm-lock.yaml* ./

# 安装前端依赖（包含开发依赖用于构建）
RUN pnpm install --frozen-lockfile || pnpm install

# 复制前端源码
COPY frontend/ ./

# 构建前端
RUN npm run build

# Python 后端镜像
FROM python:3.11-slim AS backend

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖文件
COPY backend/requirements.txt ./

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端源码
COPY backend/ ./

# 从前端构建阶段复制构建结果
COPY --from=frontend-builder /app/frontend/dist ./static

# 创建必要的目录
RUN mkdir -p uploads data logs static

# 设置权限
RUN chmod -R 755 uploads data logs static

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]
