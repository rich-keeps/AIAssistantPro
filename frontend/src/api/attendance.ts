import request from '@/utils/request'
import type { AxiosResponse } from 'axios'
import type { ExcelPreview } from '@/types'

export interface UploadResponse {
    success: boolean
    message?: string
    data: ExcelPreview
}

export const attendanceApi = {
    /**
     * 上传Excel文件
     * @param file 文件对象
     * @returns 上传响应
     */
    uploadFile(file: File): Promise<AxiosResponse<UploadResponse>> {
        const formData = new FormData()
        formData.append('file', file)
        return request({
            url: '/api/upload',
            method: 'post',
            data: formData,
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    /**
     * 删除文件
     * @param fileId 文件ID
     */
    deleteFile(fileId: string): Promise<AxiosResponse> {
        return request({
            url: `/api/file/${fileId}`,
            method: 'delete'
        })
    },

    /**
     * 导出加班记录
     * @param fileId 文件ID
     */
    exportOvertime(fileId: string): Promise<AxiosResponse<Blob>> {
        return request({
            url: '/api/export/overtime',
            method: 'post',
            data: { file_ids: [fileId] },
            responseType: 'blob'
        })
    },

    /**
     * 导出请假记录
     * @param fileId 文件ID
     */
    exportLeave(fileId: string): Promise<AxiosResponse<Blob>> {
        return request({
            url: '/api/export/leave',
            method: 'post',
            data: { file_ids: [fileId] },
            responseType: 'blob'
        })
    },

    /**
     * 导出考勤记录
     * @param fileIds 文件ID列表
     */
    exportAttendance(fileIds: string[]): Promise<AxiosResponse<Blob>> {
        return request({
            url: '/api/export/attendance',
            method: 'post',
            data: { file_ids: fileIds },
            responseType: 'blob'
        })
    },

    /**
     * 导出合并后的请假记录
     * @param fileIds 请假记录文件ID列表
     */
    exportMergedLeaveRecords(fileIds: string[]): Promise<AxiosResponse<Blob>> {
        return request({
            url: '/api/export/merged-leave',
            method: 'post',
            data: { file_ids: fileIds },
            responseType: 'blob'
        })
    }
} 