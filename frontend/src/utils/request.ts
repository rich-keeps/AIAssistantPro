import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const service: AxiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api', // API 基础URL
    timeout: 30000, // 请求超时时间
    headers: {
        'Content-Type': 'application/json;charset=utf-8'
    }
})

// 请求拦截器
service.interceptors.request.use(
    (config) => {
        // 在这里可以添加token等认证信息
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// 响应拦截器
service.interceptors.response.use(
    (response: AxiosResponse) => {
        // 如果是下载文件，直接返回response
        if (response.config.responseType === 'blob') {
            return response
        }
        return response.data
    },
    (error) => {
        // 处理错误响应
        if (error.response) {
            const { status, data } = error.response
            let message = '请求失败'

            if (typeof data === 'string') {
                message = data
            } else if (data.detail) {
                message = data.detail
            } else if (data.message) {
                message = data.message
            }

            switch (status) {
                case 400:
                    ElMessage.error(message || '请求参数错误')
                    break
                case 401:
                    ElMessage.error('未授权，请重新登录')
                    break
                case 403:
                    ElMessage.error('拒绝访问')
                    break
                case 404:
                    ElMessage.error('请求错误，未找到该资源')
                    break
                case 500:
                    ElMessage.error('服务器错误')
                    break
                default:
                    ElMessage.error(message || `连接错误${status}`)
            }
        } else {
            ElMessage.error('网络连接异常，请稍后重试')
        }
        return Promise.reject(error)
    }
)

// 导出封装的请求方法
const request = <T = any>(config: AxiosRequestConfig): Promise<T> => {
    return service(config) as unknown as Promise<T>
}

export default request 