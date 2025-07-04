#!/bin/bash

# AI智能化管理系统停止脚本

set -e

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

# 检查Docker Compose版本
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    else
        DOCKER_COMPOSE_CMD=""
    fi
}

# 停止Docker服务
stop_docker_services() {
    log_info "停止Docker服务..."

    check_docker_compose

    if [ -f "docker-compose.yml" ] && [ ! -z "$DOCKER_COMPOSE_CMD" ]; then
        $DOCKER_COMPOSE_CMD down
        log_success "Docker服务已停止"
    else
        log_warning "未找到docker-compose.yml文件或Docker Compose未安装"
    fi
}

# 停止开发环境服务
stop_dev_services() {
    log_info "停止开发环境服务..."
    
    # 停止后端服务
    if [ -f "backend.pid" ]; then
        local backend_pid=$(cat backend.pid)
        if kill -0 $backend_pid 2>/dev/null; then
            kill $backend_pid
            log_success "后端服务已停止 (PID: $backend_pid)"
        else
            log_warning "后端服务进程不存在"
        fi
        rm -f backend.pid
    fi
    
    # 停止前端服务
    if [ -f "frontend.pid" ]; then
        local frontend_pid=$(cat frontend.pid)
        if kill -0 $frontend_pid 2>/dev/null; then
            kill $frontend_pid
            log_success "前端服务已停止 (PID: $frontend_pid)"
        else
            log_warning "前端服务进程不存在"
        fi
        rm -f frontend.pid
    fi
    
    # 查找并停止可能的残留进程
    local backend_processes=$(pgrep -f "python.*main.py" || true)
    if [ ! -z "$backend_processes" ]; then
        echo $backend_processes | xargs kill
        log_info "清理残留的后端进程"
    fi
    
    local frontend_processes=$(pgrep -f "npm.*dev" || true)
    if [ ! -z "$frontend_processes" ]; then
        echo $frontend_processes | xargs kill
        log_info "清理残留的前端进程"
    fi
}

# 清理临时文件
cleanup_temp_files() {
    log_info "清理临时文件..."
    
    # 清理上传的临时文件（保留最近的文件）
    if [ -d "uploads/temp" ]; then
        find uploads/temp -type f -mtime +1 -delete 2>/dev/null || true
        log_info "清理临时上传文件"
    fi
    
    # 清理日志文件（保留最近的日志）
    if [ -d "logs" ]; then
        find logs -name "*.log" -size +100M -delete 2>/dev/null || true
        log_info "清理大型日志文件"
    fi
    
    # 清理Python缓存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    log_success "临时文件清理完成"
}

# 显示状态
show_status() {
    echo ""
    log_info "服务状态检查..."
    
    # 检查Docker容器状态
    if command -v docker &> /dev/null; then
        local containers=$(docker ps --filter "name=adrian-oa" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || true)
        if [ ! -z "$containers" ]; then
            echo "Docker容器状态:"
            echo "$containers"
        else
            echo "没有运行中的Docker容器"
        fi
    fi
    
    # 检查端口占用
    local port_8000=$(lsof -ti:8000 2>/dev/null || true)
    local port_3000=$(lsof -ti:3000 2>/dev/null || true)
    local port_80=$(lsof -ti:80 2>/dev/null || true)
    
    if [ ! -z "$port_8000" ]; then
        log_warning "端口 8000 仍被占用 (PID: $port_8000)"
    fi
    
    if [ ! -z "$port_3000" ]; then
        log_warning "端口 3000 仍被占用 (PID: $port_3000)"
    fi
    
    if [ ! -z "$port_80" ]; then
        log_warning "端口 80 仍被占用 (PID: $port_80)"
    fi
    
    if [ -z "$port_8000" ] && [ -z "$port_3000" ] && [ -z "$port_80" ]; then
        log_success "所有服务端口已释放"
    fi
}

# 主函数
main() {
    local cleanup_option=${1:-normal}
    
    echo "========================================"
    echo "   AI智能化管理系统停止脚本"
    echo "========================================"
    echo ""
    
    # 停止Docker服务
    stop_docker_services
    
    # 停止开发环境服务
    stop_dev_services
    
    # 根据选项决定是否清理
    if [ "$cleanup_option" = "clean" ]; then
        cleanup_temp_files
    fi
    
    # 显示状态
    show_status
    
    echo ""
    log_success "所有服务已停止"
    
    if [ "$cleanup_option" != "clean" ]; then
        echo ""
        log_info "如需清理临时文件，请运行: $0 clean"
    fi
}

# 脚本入口
main "$@"
