# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import report, routes, settings, invoice

app = FastAPI(
    title="Excel数据处理工具",
    description="一个用于处理Excel文件的RESTful API服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许前端开发服务器的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(routes.router, prefix="/api", tags=["Excel处理"])
app.include_router(report.router, prefix="/api/report", tags=["报表生成"])
app.include_router(settings.router, prefix="/api/settings", tags=["系统设置"])
app.include_router(invoice.router, prefix="/api/invoice", tags=["发票处理"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
