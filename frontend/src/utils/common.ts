import dayjs from 'dayjs'

/**
 * 从响应头的Content-Disposition中提取文件名
 * @param headers 响应头
 * @returns 提取的文件名，如果没有则返回null
 */
export const getFilenameFromHeaders = (headers: any): string | null => {
    const contentDisposition = headers['content-disposition'] || headers['Content-Disposition']
    if (!contentDisposition) return null

    // 尝试从Content-Disposition中提取文件名
    const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
    const matches = filenameRegex.exec(contentDisposition)
    if (matches && matches[1]) {
        // 去除引号并解码URL编码的文件名
        let filename = matches[1].replace(/['"]/g, '')
        try {
            // 尝试解码URL编码的文件名
            return decodeURIComponent(filename)
        } catch (e) {
            // 如果解码失败，直接返回原始文件名
            return filename
        }
    }
    return null
}

/**
 * 下载文件
 * @param blob 文件二进制数据
 * @param filename 文件名
 */
export const downloadFile = (blob: Blob, filename: string): void => {
    const url = window.URL.createObjectURL(
        new Blob([blob], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
    )
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
}

/**
 * 判断是否为工作日（周一至周五）
 * @param date 日期对象
 * @returns boolean
 */
export const isWorkday = (date: dayjs.Dayjs): boolean => {
    const day = date.day()
    return day !== 0 && day !== 6
}

/**
 * 获取指定月份的所有日期
 * @param year 年份
 * @param month 月份
 * @returns Array<{date: string, label: string, isWorkday: boolean}>
 */
export const getMonthDays = (year: number, month: number) => {
    const daysInMonth = new Date(year, month, 0).getDate()
    const days = []

    for (let i = 1; i <= daysInMonth; i++) {
        const currentDate = dayjs(`${year}-${month}-${i}`)
        const dateStr = currentDate.format('YYYY-MM-DD')
        const workday = isWorkday(currentDate)

        days.push({
            date: dateStr,
            label: `${i}日 ${currentDate.format('ddd')}`,
            isWorkday: workday
        })
    }

    return days
}

/**
 * 格式化日期
 * @param date Date对象
 * @param format 格式化模式
 * @returns string
 */
export const formatDate = (date: Date, format: string = 'YYYY-MM-DD'): string => {
    return dayjs(date).format(format)
}
