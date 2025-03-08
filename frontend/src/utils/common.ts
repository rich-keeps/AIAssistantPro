import dayjs from 'dayjs'
import { holidayApi } from '@/api/holiday'

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

// 节假日数据缓存
interface HolidayCache {
    [year: number]: {
        holidays: string[];
        workdaysOnWeekends: string[];
        timestamp: number;
    }
}

// 缓存过期时间（24小时）
const CACHE_EXPIRATION = 24 * 60 * 60 * 1000;

// 初始化缓存
const holidayCache: HolidayCache = {};

/**
 * 获取节假日数据
 * @param year 年份
 * @returns Promise<{holidays: string[], workdaysOnWeekends: string[]}>
 */
export const getHolidayData = async (year: number) => {
    // 检查缓存是否存在且未过期
    const now = Date.now();
    const cachedData = holidayCache[year];

    if (cachedData && (now - cachedData.timestamp < CACHE_EXPIRATION)) {
        return {
            holidays: cachedData.holidays,
            workdaysOnWeekends: cachedData.workdaysOnWeekends
        };
    }

    try {
        // 从API获取数据
        const response = await holidayApi.getHolidayData(year);

        // 更新缓存
        holidayCache[year] = {
            holidays: response.holidays,
            workdaysOnWeekends: response.workdaysOnWeekends,
            timestamp: now
        };

        return {
            holidays: response.holidays,
            workdaysOnWeekends: response.workdaysOnWeekends
        };
    } catch (error) {
        console.error('获取节假日数据失败:', error);

        // 如果API请求失败但有过期的缓存，仍然使用它
        if (cachedData) {
            return {
                holidays: cachedData.holidays,
                workdaysOnWeekends: cachedData.workdaysOnWeekends
            };
        }

        // 如果没有缓存，返回空数组
        return {
            holidays: [],
            workdaysOnWeekends: []
        };
    }
};

/**
 * 判断是否为工作日（周一至周五，不是法定节假日，或者是调休工作日）
 * @param date 日期对象
 * @returns Promise<boolean>
 */
export const isWorkday = async (date: dayjs.Dayjs): Promise<boolean> => {
    const dateStr = date.format('YYYY-MM-DD');
    const day = date.day();
    const year = date.year();

    try {
        // 获取节假日数据
        const { holidays, workdaysOnWeekends } = await getHolidayData(year);

        // 如果是法定节假日，则不是工作日
        if (holidays.includes(dateStr)) {
            return false;
        }

        // 如果是调休工作日（周末但需要上班），则是工作日
        if (workdaysOnWeekends.includes(dateStr)) {
            return true;
        }

        // 正常工作日判断（周一至周五）
        return day !== 0 && day !== 6;
    } catch (error) {
        console.error('判断工作日失败:', error);
        // 出错时，使用基本的工作日判断（周一至周五）
        return day !== 0 && day !== 6;
    }
};

// 同步版本的isWorkday函数，用于不支持异步的场景
export const isWorkdaySync = (date: dayjs.Dayjs): boolean => {
    const day = date.day();
    // 简单判断周一至周五
    return day !== 0 && day !== 6;
};

/**
 * 获取指定月份的所有日期
 * @param year 年份
 * @param month 月份
 * @returns Promise<Array<{date: string, label: string, isWorkday: boolean}>>
 */
export const getMonthDays = async (year: number, month: number) => {
    const daysInMonth = new Date(year, month, 0).getDate();
    const days = [];

    try {
        // 获取节假日数据
        const { holidays, workdaysOnWeekends } = await getHolidayData(year);

        for (let i = 1; i <= daysInMonth; i++) {
            const currentDate = dayjs(`${year}-${month}-${i}`);
            const dateStr = currentDate.format('YYYY-MM-DD');
            const day = currentDate.day();

            // 判断是否为工作日
            let workday = day !== 0 && day !== 6; // 默认周一至周五是工作日

            // 如果是法定节假日，则不是工作日
            if (holidays.includes(dateStr)) {
                workday = false;
            }

            // 如果是调休工作日，则是工作日
            if (workdaysOnWeekends.includes(dateStr)) {
                workday = true;
            }

            days.push({
                date: dateStr,
                label: `${i}日 ${currentDate.format('ddd')}`,
                isWorkday: workday
            });
        }
    } catch (error) {
        console.error('获取月份日期失败:', error);

        // 如果API请求失败，使用基本的工作日判断
        for (let i = 1; i <= daysInMonth; i++) {
            const currentDate = dayjs(`${year}-${month}-${i}`);
            const dateStr = currentDate.format('YYYY-MM-DD');
            const day = currentDate.day();

            days.push({
                date: dateStr,
                label: `${i}日 ${currentDate.format('ddd')}`,
                isWorkday: day !== 0 && day !== 6 // 简单判断周一至周五
            });
        }
    }

    return days;
};

/**
 * 格式化日期
 * @param date Date对象
 * @param format 格式化模式
 * @returns string
 */
export const formatDate = (date: Date, format: string = 'YYYY-MM-DD'): string => {
    return dayjs(date).format(format)
}
