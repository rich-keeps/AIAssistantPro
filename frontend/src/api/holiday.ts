import request from '@/utils/request'

/**
 * 节假日API接口
 */
export const holidayApi = {
    /**
     * 获取指定年份的节假日和调休工作日信息
     * @param year 年份
     * @returns Promise<{holidays: string[], workdaysOnWeekends: string[]}>
     */
    getHolidayData(year: number) {
        return request({
            url: '/api/holidays',
            method: 'get',
            params: { year }
        })
    }
} 