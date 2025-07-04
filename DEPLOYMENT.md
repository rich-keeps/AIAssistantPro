# AI 智能化管理系统部署指南

## 概述

本文档提供了 AI 智能化管理系统的完整部署指南，支持开发环境和生产环境的一键部署。

**特别说明**: 本系统专为公司内网环境设计，支持 IP 地址直接访问，无需域名和 SSL 证书配置。

## 系统要求

### 基础要求

-   **操作系统**: Linux (推荐 Ubuntu 20.04+), macOS, Windows
-   **Docker**: 20.10+
-   **Docker Compose**: 2.0+
-   **Git**: 2.0+

### 开发环境额外要求

-   **Node.js**: 18.0.0+ (推荐 20.0.0+)
-   **Python**: 3.11.8
-   **npm**: 8.0+

## 快速部署

### 1. 克隆项目

```bash
git clone <repository-url>
cd adrian-oa
```

### 2. 一键部署

#### 开发环境部署

```bash
./deploy.sh dev
```

#### 生产环境部署

```bash
./deploy.sh prod
```

### 3. 停止服务

```bash
# 普通停止
./stop.sh

# 停止并清理临时文件
./stop.sh clean
```

## 详细部署说明

### 开发环境部署

开发环境使用本地 Python 和 Node.js 环境，适合开发和调试。

1. **后端部署**:

    - 自动创建 Python 虚拟环境
    - 安装 Python 依赖
    - 启动 FastAPI 开发服务器 (端口 8000)

2. **前端部署**:

    - 安装 Node.js 依赖
    - 启动 Vite 开发服务器 (端口 3000)

3. **访问地址**:
    - 前端: http://localhost:3000
    - 后端 API: http://localhost:8000
    - API 文档: http://localhost:8000/docs

### 生产环境部署

生产环境使用 Docker 容器化部署，包含 Nginx 反向代理。

1. **容器服务**:

    - **app**: 主应用容器 (FastAPI + 前端静态文件)
    - **nginx**: 反向代理和静态文件服务

2. **端口映射**:

    - HTTP: 80
    - 应用: 8000 (内部)

3. **访问地址** (自动获取服务器 IP):
    - 前端: http://服务器 IP (如: http://192.168.1.100)
    - 前端: http://localhost (本地访问)
    - API 文档: http://服务器 IP/docs
    - 健康检查: http://服务器 IP/health

## 配置说明

### 环境变量配置

#### 后端配置文件

-   **开发环境**: `backend/.env`
-   **生产环境**: `backend/.env.production`

主要配置项:

```bash
ENVIRONMENT=production          # 环境类型
DEBUG=False                    # 调试模式
HOST=0.0.0.0                  # 监听地址
PORT=8000                     # 监听端口
SECRET_KEY=your-secret-key    # 安全密钥
CORS_ORIGINS=["*"]  # 内网环境允许所有跨域源
```

#### 前端配置文件

-   **开发环境**: `frontend/.env`
-   **生产环境**: `frontend/.env.production`

主要配置项:

```bash
VITE_API_BASE_URL=http://服务器IP  # API基础URL (部署时自动设置)
VITE_APP_TITLE=AI智能化管理系统           # 应用标题
VITE_MAX_UPLOAD_SIZE=52428800             # 最大上传大小
```

### Docker 配置

#### Dockerfile

-   多阶段构建，优化镜像大小
-   前端构建 + 后端运行环境
-   非 root 用户运行，提高安全性
-   内置健康检查

#### docker-compose.yml

-   应用容器 + Nginx 容器
-   数据卷持久化
-   网络隔离
-   自动重启策略

### Nginx 配置

#### 主要功能

-   反向代理到后端 API
-   静态文件服务
-   Gzip 压缩
-   缓存控制
-   SSL 终止 (可选)

#### 配置文件: `nginx.conf`

-   上游服务器配置
-   路由规则
-   安全头设置
-   日志配置

## 内网生产环境配置清单

### 部署前准备

1. **服务器准备**:

    ```bash
    # 确保服务器防火墙开放80端口
    sudo ufw allow 80

    # 检查服务器IP地址
    ip addr show
    ```

2. **自动配置** (部署脚本自动完成):

    ```bash
    # 系统会自动获取服务器IP并配置前端API地址
    # 无需手动修改域名和SSL配置
    # 所有配置已优化为内网IP访问模式
    ```

3. **内网访问验证**:

    ```bash
    # 部署完成后，其他内网用户可通过以下地址访问
    # http://服务器IP (如: http://192.168.1.100)
    ```

### 部署后检查

1. **健康检查**:

    ```bash
    curl -f http://localhost/health
    ```

2. **服务状态**:

    ```bash
    docker-compose ps
    docker-compose logs -f
    ```

3. **端口检查**:
    ```bash
    netstat -tlnp | grep -E ':(80|443|8000)'
    ```

## 监控和维护

### 日志管理

1. **应用日志**:

    - 位置: `logs/app.log`
    - 轮转: 自动轮转，保留 5 个备份

2. **Nginx 日志**:

    - 访问日志: `/var/log/nginx/access.log`
    - 错误日志: `/var/log/nginx/error.log`

3. **Docker 日志**:

    ```bash
    # 查看应用日志
    docker-compose logs app

    # 查看Nginx日志
    docker-compose logs nginx

    # 实时日志
    docker-compose logs -f
    ```

### 备份策略

1. **数据备份**:

    ```bash
    # 备份上传文件
    tar -czf backup-uploads-$(date +%Y%m%d).tar.gz uploads/

    # 备份配置数据
    tar -czf backup-data-$(date +%Y%m%d).tar.gz data/
    ```

2. **配置备份**:
    ```bash
    # 备份配置文件
    tar -czf backup-config-$(date +%Y%m%d).tar.gz *.env *.conf *.yml
    ```

### 更新部署

1. **拉取最新代码**:

    ```bash
    git pull origin main
    ```

2. **重新部署**:

    ```bash
    ./stop.sh
    ./deploy.sh prod
    ```

3. **滚动更新** (零停机):
    ```bash
    docker-compose up -d --no-deps app
    ```

## 故障排除

### 常见问题

1. **端口被占用**:

    ```bash
    # 查找占用进程
    lsof -ti:8000

    # 停止进程
    ./stop.sh clean
    ```

2. **Docker 构建失败**:

    ```bash
    # 清理Docker缓存
    docker system prune -a

    # 重新构建
    docker-compose build --no-cache
    ```

3. **权限问题**:

    ```bash
    # 修复目录权限
    chmod -R 755 uploads data logs
    chown -R $USER:$USER uploads data logs
    ```

4. **OCR 功能异常**:

    ```bash
    # 检查PaddleOCR版本
    pip show paddleocr

    # 重新安装兼容版本
    pip install paddleocr==2.7.3
    ```

### 性能优化

1. **资源限制**:

    ```yaml
    # docker-compose.yml
    deploy:
        resources:
            limits:
                memory: 2G
                cpus: '1.0'
    ```

2. **缓存配置**:

    - 启用 Redis 缓存 (可选)
    - 配置 Nginx 缓存
    - 优化静态资源缓存

3. **数据库优化** (如果使用):
    - 连接池配置
    - 索引优化
    - 查询优化

## 安全建议

1. **网络安全**:

    - 配置防火墙规则
    - 使用 HTTPS
    - 定期更新 SSL 证书

2. **应用安全**:

    - 定期更新依赖
    - 配置安全头
    - 限制文件上传大小和类型

3. **访问控制**:
    - 配置访问日志
    - 实施 IP 白名单 (如需要)
    - 监控异常访问

## 联系支持

如遇到部署问题，请提供以下信息：

-   操作系统版本
-   Docker 版本
-   错误日志
-   部署步骤

---

**注意**: 生产环境部署前，请务必修改所有默认配置，包括域名、密钥、证书等。
