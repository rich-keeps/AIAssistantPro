# 考勤管理系统

## 项目简介
这是一个基于Vue 3 + FastAPI的现代考勤管理系统，提供Excel文件导入、数据可视化展示、考勤记录管理等功能。系统采用前后端分离架构，提供简洁直观的用户界面和高效的数据处理能力。

## 功能特性
1. Excel文件导入
   - 支持.xlsx/.xls格式文件导入
   - 文件预览功能
   - 拖拽上传
   - 文件格式验证

2. 数据展示功能
   - 分页表格展示
   - 自动识别数据格式
   - 表格列宽自适应
   - 数据排序和筛选

3. 考勤管理功能
   - 加班记录管理
   - 请假记录管理
   - 考勤统计报表
   - 数据导出功能

4. 系统功能
   - 响应式界面设计
   - 错误处理和提示
   - 数据验证
   - 操作日志记录

## 技术栈
### 前端技术
- Vue 3 - 用户界面框架
- TypeScript - 类型安全的JavaScript超集
- Element Plus - UI组件库
- Vue Router - 路由管理
- Pinia - 状态管理
- Axios - HTTP客户端
- XLSX - Excel文件处理
- Vite - 构建工具

### 后端技术
- Python 3.8+ - 主要开发语言
- FastAPI - Web框架
- Pandas - 数据处理
- openpyxl - Excel文件操作
- python-multipart - 文件上传处理
- python-dotenv - 环境变量管理

## 项目结构
```
project/
├── frontend/                # 前端项目目录
│   ├── src/
│   │   ├── assets/         # 静态资源
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # 状态管理
│   │   ├── types/          # TypeScript类型定义
│   │   ├── utils/          # 工具函数
│   │   └── App.vue         # 根组件
│   ├── public/             # 公共资源
│   └── index.html          # HTML模板
├── backend/                 # 后端项目目录
│   ├── api/                # API接口
│   │   └── routes/         # 路由定义
│   ├── core/               # 核心功能
│   │   ├── config.py       # 配置管理
│   │   └── security.py     # 安全相关
│   ├── models/             # 数据模型
│   ├── services/           # 业务逻辑
│   ├── utils/              # 工具函数
│   └── main.py            # 应用入口
```

## 环境要求
- Node.js 16+
- Python 3.8+
- Git

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
1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
2. **运行开发服务器**
   ```bash
   python main.py
   ```
 

## 部署指南
1. **前端部署**
   ```bash
   cd frontend
   npm run build
   ```
   将dist目录下的文件部署到Web服务器

2. **后端部署**
   ```bash
   cd backend
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

## 开发规范
1. **Git提交规范**
   - feat: 新功能
   - fix: 修复bug
   - docs: 文档更新
   - style: 代码格式化
   - refactor: 代码重构
   - test: 测试相关
   - chore: 构建过程或辅助工具的变动

2. **代码规范**
   - 前端遵循Vue 3风格指南
   - 后端遵循PEP 8规范
   - 使用TypeScript类型注解
   - 编写单元测试

## 常见问题
1. **前端开发环境启动失败**
   - 检查Node.js版本是否满足要求
   - 删除node_modules后重新安装依赖
   - 检查.env文件配置是否正确

2. **后端开发环境启动失败**
   - 检查Python版本是否满足要求
   - 确认虚拟环境是否正确激活
   - 检查依赖是否完整安装
   - 检查.env文件配置是否正确

 