# AI 智能化管理系统

## 项目简介

这是一个基于 Vue 3 + FastAPI 的现代化智能管理系统，集成了考勤管理、发票识别 OCR、数据处理等多种功能。系统采用前后端分离架构，提供简洁直观的用户界面和高效的数据处理能力，支持多种文件格式的智能识别和处理。

## 功能特性

### 1. 考勤管理模块

-   **Excel 文件导入**

    -   支持.xlsx/.xls 格式文件导入
    -   文件预览功能
    -   拖拽上传
    -   文件格式验证

-   **数据展示功能**

    -   分页表格展示
    -   自动识别数据格式
    -   表格列宽自适应
    -   数据排序和筛选

-   **考勤记录管理**
    -   加班记录管理
    -   请假记录管理
    -   考勤统计报表
    -   数据导出功能

### 2. 发票识别 OCR 模块

-   **智能发票识别**

    -   支持 JPG、PNG、PDF 格式发票
    -   基于 PaddleOCR 的高精度文字识别
    -   自动提取发票金额、发票号码等关键信息
    -   支持增值税专用发票、普通发票等多种类型

-   **图像处理功能**
    -   自动图像预处理和优化
    -   支持倾斜文本自动校正
    -   多种图像格式兼容
    -   PDF 文档自动转换

### 3. 报表生成模块

-   **智能报表生成**
    -   考勤数据统计分析
    -   自定义报表模板
    -   多格式导出（Excel、PDF 等）
    -   数据可视化图表

### 4. 系统功能

-   响应式界面设计
-   错误处理和提示
-   数据验证
-   操作日志记录
-   系统设置管理

## 技术栈

### 前端技术

-   **Vue 3** - 用户界面框架
-   **TypeScript** - 类型安全的 JavaScript 超集
-   **Element Plus** - UI 组件库
-   **Vue Router** - 路由管理
-   **Pinia** - 状态管理
-   **Axios** - HTTP 客户端
-   **XLSX** - Excel 文件处理
-   **Vite** - 构建工具

### 后端技术

-   **Python 3.11.8** - 主要开发语言
-   **FastAPI** - Web 框架
-   **Uvicorn** - ASGI 服务器

### 数据处理

-   **Pandas** - 数据分析和处理
-   **openpyxl** - Excel 文件操作
-   **xlsxwriter** - Excel 文件生成
-   **python-dateutil** - 日期处理
-   **chinese-calendar** - 中国节假日处理

### OCR 和图像处理

-   **PaddleOCR** - 文字识别引擎
-   **PaddlePaddle** - 深度学习框架
-   **OpenCV** - 计算机视觉库
-   **Pillow** - 图像处理库
-   **pdf2image** - PDF 转图像
-   **pytesseract** - 备用 OCR 引擎

### 其他工具

-   **python-multipart** - 文件上传处理
-   **python-dotenv** - 环境变量管理
-   **pydantic** - 数据验证
-   **pytest** - 测试框架

## 项目结构

```
adrian-oa/
├── frontend/                    # 前端项目目录
│   ├── src/
│   │   ├── api/                # API 接口定义
│   │   │   ├── attendance.ts   # 考勤相关 API
│   │   │   ├── holiday.ts      # 节假日 API
│   │   │   └── report.ts       # 报表 API
│   │   ├── config/             # 配置文件
│   │   ├── router/             # 路由配置
│   │   ├── types/              # TypeScript 类型定义
│   │   ├── utils/              # 工具函数
│   │   ├── views/              # 页面组件
│   │   │   ├── ExcelProcessor.vue  # 考勤管理页面
│   │   │   ├── Report.vue      # 报表生成页面
│   │   │   └── Settings.vue    # 系统设置页面
│   │   ├── App.vue             # 根组件
│   │   └── main.ts             # 应用入口
│   ├── public/                 # 公共资源
│   ├── index.html              # HTML 模板
│   ├── package.json            # 依赖配置
│   └── vite.config.ts          # Vite 配置
├── backend/                     # 后端项目目录
│   ├── api/                    # API 接口
│   │   ├── routes.py           # 考勤管理路由
│   │   ├── report.py           # 报表生成路由
│   │   ├── invoice.py          # 发票识别路由
│   │   ├── holiday.py          # 节假日路由
│   │   └── settings.py         # 系统设置路由
│   ├── core/                   # 核心功能
│   ├── models/                 # 数据模型
│   │   └── schemas.py          # Pydantic 模型
│   ├── services/               # 业务逻辑
│   │   ├── excel_service.py    # Excel 处理服务
│   │   ├── invoice_service.py  # 发票识别服务
│   │   └── report_service.py   # 报表生成服务
│   ├── utils/                  # 工具函数
│   ├── uploads/                # 文件上传目录
│   ├── main.py                 # 应用入口
│   └── requirements.txt        # Python 依赖
└── README.md                   # 项目文档
```

## 环境要求

-   **Node.js** 18.0.0+ (推荐 20.0.0+)
-   **Python** 3.11.8
-   **Git** 版本控制
-   **系统要求**：支持 macOS、Linux、Windows

## 开发环境搭建

### 前端开发环境

1. **安装依赖**

    ```bash
    cd frontend
    npm install
    ```

2. **开发模式运行**

    ```bash
    npm run dev
    ```

3. **代码格式化**

    ```bash
    npm run format
    ```

4. **代码检查**

    ```bash
    npm run lint
    ```

5. **运行测试**
    ```bash
    npm run test:unit
    ```

### 后端开发环境

1. **创建虚拟环境**

    ```bash
    cd backend
    python -m venv venv
    ```

2. **激活虚拟环境**

    - Windows:
        ```bash
        venv\\Scripts\\activate
        ```
    - macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3. **安装依赖**

    ```bash
    pip install -r requirements.txt
    ```

4. **配置环境变量**
   复制.env.example 为.env 并根据需要修改配置

5. **运行开发服务器**
    ```bash
    python3 main.py
    ```
    或者使用 uvicorn：
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

## API 文档

启动后端服务后，访问以下地址查看 API 文档：

-   **Swagger UI**: http://localhost:8000/docs
-   **ReDoc**: http://localhost:8000/redoc

### 主要 API 端点

-   **考勤管理**: `/api/upload` - Excel 文件上传和处理
-   **发票识别**: `/api/invoice/upload` - 发票文件上传和 OCR 识别
-   **报表生成**: `/api/report/` - 各类报表生成
-   **系统设置**: `/api/settings/` - 系统配置管理
-   **节假日查询**: `/api/holiday/` - 节假日信息查询

## 部署指南

### 生产环境部署

1. **前端部署**

    ```bash
    cd frontend
    npm run build
    ```

    将 `dist` 目录下的文件部署到 Web 服务器（如 Nginx）

2. **后端部署**

    ```bash
    cd backend
    # 安装生产环境依赖
    pip3 install -r requirements.txt
    pip3 install gunicorn

    # 启动生产服务器
    gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    ```

### 开发环境快速启动

1. **启动后端服务**

    ```bash
    cd backend
    python3 main.py
    ```

2. **启动前端服务**

    ```bash
    cd frontend
    npm run dev
    ```

3. **访问应用**
    - 前端地址：http://localhost:3000
    - 后端 API：http://localhost:8000
    - API 文档：http://localhost:8000/docs

## 开发规范

1. **Git 提交规范**

    - feat: 新功能
    - fix: 修复 bug
    - docs: 文档更新
    - style: 代码格式化
    - refactor: 代码重构
    - test: 测试相关
    - chore: 构建过程或辅助工具的变动

2. **代码规范**
    - 前端遵循 Vue 3 风格指南
    - 后端遵循 PEP 8 规范
    - 使用 TypeScript 类型注解
    - 编写单元测试
