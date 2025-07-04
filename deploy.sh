#!/bin/bash

# AI智能化管理系统一键部署脚本
# 使用方法: ./deploy.sh [dev|prod]

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 检查Docker Compose版本
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
        log_info "使用 Docker Compose V1"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
        log_info "使用 Docker Compose V2"
    else
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
}

# 检查系统要求
check_requirements() {
    log_info "检查系统要求..."

    # 检查必需的命令
    check_command "docker"
    check_docker_compose
    check_command "git"
    
    # 检查Docker是否运行
    if ! docker info &> /dev/null; then
        log_error "Docker 未运行，请启动 Docker"
        exit 1
    fi
    
    log_success "系统要求检查通过"
}

# 环境设置
setup_environment() {
    local env_type=$1
    log_info "设置 $env_type 环境..."
    
    if [ "$env_type" = "prod" ]; then
        # 生产环境配置
        if [ ! -f "backend/.env.production" ]; then
            log_error "生产环境配置文件 backend/.env.production 不存在"
            exit 1
        fi
        cp backend/.env.production backend/.env
        export ENVIRONMENT=production
        export DEBUG=False
    else
        # 开发环境配置
        export ENVIRONMENT=development
        export DEBUG=True
    fi
    
    log_success "环境设置完成"
}

# 构建应用
build_application() {
    log_info "构建应用..."

    # 停止现有容器
    $DOCKER_COMPOSE_CMD down 2>/dev/null || true

    # 构建镜像
    $DOCKER_COMPOSE_CMD build --no-cache

    log_success "应用构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 创建必要的目录
    mkdir -p uploads data logs ssl
    
    # 设置目录权限
    chmod 755 uploads data logs
    
    # 启动服务
    $DOCKER_COMPOSE_CMD up -d
    
    log_success "服务启动完成"
}

# 健康检查
health_check() {
    log_info "进行健康检查..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            log_success "健康检查通过"
            return 0
        fi
        
        log_info "等待服务启动... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    log_error "健康检查失败，服务可能未正常启动"
    return 1
}

# 获取服务器IP地址
get_server_ip() {
    # macOS和Linux兼容的IP获取方法
    local server_ip=""

    # 方法1: 使用route命令 (macOS)
    if command -v route &> /dev/null; then
        server_ip=$(route get default 2>/dev/null | grep interface | awk '{print $2}' | head -1)
        if [ ! -z "$server_ip" ]; then
            server_ip=$(ifconfig "$server_ip" 2>/dev/null | grep 'inet ' | awk '{print $2}' | head -1)
        fi
    fi

    # 方法2: 使用ip命令 (Linux)
    if [ -z "$server_ip" ] && command -v ip &> /dev/null; then
        server_ip=$(ip route get 1.1.1.1 2>/dev/null | grep -o 'src [0-9.]*' | awk '{print $2}')
    fi

    # 方法3: 使用hostname命令
    if [ -z "$server_ip" ]; then
        server_ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    fi

    # 方法4: 使用ifconfig命令
    if [ -z "$server_ip" ] && command -v ifconfig &> /dev/null; then
        server_ip=$(ifconfig | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | head -1)
    fi

    # 默认值
    if [ -z "$server_ip" ]; then
        server_ip="localhost"
    fi

    echo "$server_ip"
}

# 更新前端API配置
update_frontend_config() {
    local server_ip=$1
    log_info "更新前端API配置为: http://$server_ip"

    # 更新前端生产环境配置
    if [ -f "frontend/.env.production" ]; then
        sed -i.bak "s|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=http://$server_ip|g" frontend/.env.production
        log_success "前端API配置已更新"
    fi
}

# 显示部署信息
show_deployment_info() {
    local env_type=$1
    local server_ip=$(get_server_ip)

    echo ""
    log_success "部署完成！"
    echo ""
    echo "访问地址："
    echo "  前端应用: http://$server_ip"
    echo "  前端应用: http://localhost (本地访问)"
    echo "  API文档:  http://$server_ip/docs"
    echo "  健康检查: http://$server_ip/health"
    echo ""
    echo "管理命令："
    echo "  查看日志: $DOCKER_COMPOSE_CMD logs -f"
    echo "  停止服务: $DOCKER_COMPOSE_CMD down"
    echo "  重启服务: $DOCKER_COMPOSE_CMD restart"
    echo ""

    if [ "$env_type" = "prod" ]; then
        log_warning "内网生产环境部署注意事项："
        echo "  1. 系统已配置为支持IP访问，无需域名"
        echo "  2. 当前服务器IP: $server_ip"
        echo "  3. 请确保防火墙开放80端口"
        echo "  4. 其他内网用户可通过 http://$server_ip 访问系统"
    fi
}

# 开发环境部署
deploy_development() {
    log_info "开始开发环境部署..."
    
    setup_environment "dev"
    
    # 开发环境直接启动，不使用Docker
    log_info "启动后端服务..."
    cd backend
    
    # 检查Python环境
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    pip install -r requirements.txt
    
    # 启动后端（后台运行）
    nohup python3 main.py > ../logs/backend.log 2>&1 &
    echo $! > ../backend.pid
    
    cd ../frontend
    
    # 安装前端依赖
    if [ ! -d "node_modules" ]; then
        log_info "安装前端依赖..."
        npm install
    fi
    
    # 启动前端（后台运行）
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    echo $! > ../frontend.pid
    
    cd ..
    
    log_success "开发环境启动完成"
    echo "前端地址: http://localhost:3000"
    echo "后端API: http://localhost:8000"
}

# 生产环境部署
deploy_production() {
    log_info "开始生产环境部署..."

    check_requirements
    setup_environment "prod"

    # 获取服务器IP并更新前端配置
    local server_ip=$(get_server_ip)
    update_frontend_config "$server_ip"

    build_application
    start_services

    if health_check; then
        show_deployment_info "prod"
    else
        log_error "部署失败，请检查日志"
        $DOCKER_COMPOSE_CMD logs
        exit 1
    fi
}

# 主函数
main() {
    local env_type=${1:-dev}
    
    echo "========================================"
    echo "   AI智能化管理系统部署脚本"
    echo "========================================"
    echo ""
    
    # 创建日志目录
    mkdir -p logs
    
    case $env_type in
        "dev"|"development")
            deploy_development
            ;;
        "prod"|"production")
            deploy_production
            ;;
        *)
            log_error "无效的环境类型: $env_type"
            echo "使用方法: $0 [dev|prod]"
            exit 1
            ;;
    esac
}

# 脚本入口
main "$@"
