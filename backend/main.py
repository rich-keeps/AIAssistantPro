# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from api import report, routes, settings, invoice

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 获取环境变量
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# 根据环境设置CORS origins - 内网访问模式
if ENVIRONMENT == "production":
    CORS_ORIGINS = [
        "http://localhost",
        "http://127.0.0.1",
        "*"  # 内网环境允许所有来源
    ]
else:
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

app = FastAPI(
    title="AI智能化管理系统",
    description="集成考勤管理、发票识别OCR、数据处理的智能管理系统",
    version="1.0.0",
    debug=DEBUG
)

# 内网环境不需要严格的Host验证
# if ENVIRONMENT == "production":
#     app.add_middleware(
#         TrustedHostMiddleware,
#         allowed_hosts=["*"]  # 内网环境允许所有Host
#     )

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 静态文件服务
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": ENVIRONMENT
    }

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI智能化管理系统 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误" if ENVIRONMENT == "production" else str(exc),
            "data": None
        }
    )

# 注册路由
app.include_router(routes.router, prefix="/api", tags=["Excel处理"])
app.include_router(report.router, prefix="/api/report", tags=["报表生成"])
app.include_router(settings.router, prefix="/api/settings", tags=["系统设置"])
app.include_router(invoice.router, prefix="/api/invoice", tags=["发票处理"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=DEBUG,
        log_level="info"
    )
