import request from '@/utils/request'
import type { AxiosResponse } from 'axios'

export interface ReportGenerateParams {
    name: string
    month: string
    dates: string[]
}

/**
 * 报表生成相关API
 */
export const reportApi = {
    /**
     * 生成出差报表
     * @param data 包含姓名、月份和日期列表的请求数据
     * @returns Promise<any>
     */
    generateReport(data: any) {
        return request({
            url: '/api/report/generate',
            method: 'post',
            data,
            responseType: 'blob'
        })
    },

    /**
     * 生成报销明细表
     * @param data 包含姓名、月份和报销明细列表的请求数据
     * @returns Promise<any>
     */
    generateExpenseReport(data: any) {
        return request({
            url: '/api/report/expense',
            method: 'post',
            data,
            responseType: 'blob'
        })
    }
}

export default reportApi 