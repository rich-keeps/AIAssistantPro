import request from '@/utils/request'
import type { AxiosResponse } from 'axios'

export interface ReportGenerateParams {
    name: string
    month: string
    dates: string[]
}

export const reportApi = {
    /**
     * 生成出差报表
     * @param params 报表参数
     * @returns Blob 文件流
     */
    generateReport(params: ReportGenerateParams): Promise<AxiosResponse<Blob>> {
        return request({
            url: '/api/report/generate',
            method: 'post',
            data: params,
            responseType: 'blob'
        })
    }
}

export default reportApi 