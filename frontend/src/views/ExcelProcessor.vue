<template>
    <el-config-provider :locale="locale">
        <div class="excel-processor">
            <!-- 功能按钮区域 -->
            <div class="action-buttons">
                <el-button-group>
                    <el-button type="success" :icon="Download" @click="handleExportOvertime">
                        导出加班记录
                    </el-button>
                    <el-button type="warning" :icon="Download" @click="handleExportLeave">
                        导出请假记录
                    </el-button>
                    <el-button type="primary" :icon="Download" @click="handleExportAttendance">
                        导出考勤记录
                    </el-button>
                </el-button-group>
            </div>

            <!-- 上传区域 -->
            <div class="upload-section">
                <!-- 加班记录上传 -->
                <el-card class="upload-card">
                    <template #header>
                        <div class="card-header">
                            <h2>加班记录上传</h2>
                        </div>
                    </template>
                    <el-upload class="upload-area" drag action="/api/upload" :on-success="handleOvertimeUploadSuccess"
                        :on-error="handleUploadError" :before-upload="beforeUpload" accept=".xlsx,.xls"
                        ref="overtimeUploadRef" :on-remove="handleOvertimeUploadRemove" :file-list="overtimeFileList">
                        <el-icon class="upload-icon">
                            <Upload />
                        </el-icon>
                        <div class="upload-text">
                            <span>将加班记录文件拖到此处或<em>点击上传</em></span>
                            <p class="upload-tip">支持 .xlsx, .xls 格式文件</p>
                        </div>
                    </el-upload>
                </el-card>

                <!-- 请假记录上传 -->
                <el-card class="upload-card">
                    <template #header>
                        <div class="card-header">
                            <h2>请假记录上传</h2>
                        </div>
                    </template>
                    <el-upload class="upload-area" drag action="/api/upload" :on-success="handleLeaveUploadSuccess"
                        :on-error="handleUploadError" :before-upload="beforeUpload" accept=".xlsx,.xls"
                        ref="leaveUploadRef" :on-remove="handleLeaveUploadRemove" :file-list="leaveFileList">
                        <el-icon class="upload-icon">
                            <Upload />
                        </el-icon>
                        <div class="upload-text">
                            <span>将请假记录文件拖到此处或<em>点击上传</em></span>
                            <p class="upload-tip">支持 .xlsx, .xls 格式文件</p>
                        </div>
                    </el-upload>
                </el-card>
            </div>

            <!-- 文件列表和预览数据 -->
            <template v-for="(file, index) in fileList" :key="file.id">
                <el-card class="preview-card">
                    <template #header>
                        <div class="card-header">
                            <div class="file-info">
                                <h2>{{ file.name }}</h2>
                                <div class="file-tags">
                                    <el-tag :type="file.type === 'overtime' ? 'success' : 'warning'" size="small">
                                        {{ file.type === 'overtime' ? '加班记录' : '请假记录' }}
                                    </el-tag>
                                    <span class="total-count">共 {{ file.preview.total_rows }} 条数据</span>
                                </div>
                            </div>
                            <el-button type="danger" text @click="removeFile(index)">
                                <el-icon>
                                    <Delete />
                                </el-icon>
                                移除
                            </el-button>
                        </div>
                    </template>

                    <div class="table-wrapper">
                        <el-table :data="file.currentData" border>
                            <el-table-column v-for="header in file.headers" :key="header.key" :prop="header.key"
                                :label="header.label" :min-width="header.width" align="center" show-overflow-tooltip>
                                <template #default="scope">
                                    <span v-if="header.type === 'number'">{{ formatNumber(scope.row[header.key])
                                        }}</span>
                                    <span v-else-if="header.type === 'datetime'">{{ formatDate(scope.row[header.key])
                                        }}</span>
                                    <span v-else>{{ scope.row[header.key] }}</span>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                    <div class="pagination-container">
                        <el-pagination v-model:current-page="file.currentPage" v-model:page-size="file.pageSize"
                            :page-sizes="[10, 20, 50, 100]" :total="file.preview.total_rows"
                            layout="total, sizes, prev, pager, next"
                            @size-change="(size: number) => handleSizeChange(size, index)"
                            @current-change="(page: number) => handleCurrentChange(page, index)" />
                    </div>
                </el-card>
            </template>
        </div>
    </el-config-provider>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Upload, Delete, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { ExcelPreview, ColumnHeader } from '../types'
import type { UploadInstance, UploadFile } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const locale = zhCn
const overtimeUploadRef = ref<UploadInstance>()
const leaveUploadRef = ref<UploadInstance>()

interface FileInfo {
    id: string
    name: string
    type: 'overtime' | 'leave'  // 文件类型：加班或请假
    preview: ExcelPreview
    currentData: any[]
    headers: ColumnHeader[]
    currentPage: number
    pageSize: number
}

const fileList = ref<FileInfo[]>([])

// 计算加班记录文件列表
const overtimeFileList = computed(() => {
    return fileList.value
        .filter(file => file.type === 'overtime')
        .map(file => ({
            name: file.name,
            url: '#',
            status: 'success'
        }))
})

// 计算请假记录文件列表
const leaveFileList = computed(() => {
    return fileList.value
        .filter(file => file.type === 'leave')
        .map(file => ({
            name: file.name,
            url: '#',
            status: 'success'
        }))
})

// 处理加班记录上传成功
const handleOvertimeUploadSuccess = async (response: any, uploadFile: any) => {
    if (response.success) {
        const newFile: FileInfo = {
            id: response.data.file_id,
            name: uploadFile.name,
            type: 'overtime',
            preview: response.data,
            currentData: response.data.sample_data || [],
            headers: response.data.headers,
            currentPage: 1,
            pageSize: 10
        }
        fileList.value.push(newFile)
        ElMessage.success('加班记录上传成功')
    } else {
        ElMessage.error(response.message || '上传失败')
    }
}

// 处理请假记录上传成功
const handleLeaveUploadSuccess = async (response: any, uploadFile: any) => {
    if (response.success) {
        const newFile: FileInfo = {
            id: response.data.file_id,
            name: uploadFile.name,
            type: 'leave',
            preview: response.data,
            currentData: response.data.sample_data || [],
            headers: response.data.headers,
            currentPage: 1,
            pageSize: 10
        }
        fileList.value.push(newFile)
        ElMessage.success('请假记录上传成功')
    } else {
        ElMessage.error(response.message || '上传失败')
    }
}

// 处理加班记录移除
const handleOvertimeUploadRemove = (uploadFile: UploadFile) => {
    const index = fileList.value.findIndex(file => file.name === uploadFile.name && file.type === 'overtime')
    if (index !== -1) {
        removeFile(index)
    }
}

// 处理请假记录移除
const handleLeaveUploadRemove = (uploadFile: UploadFile) => {
    const index = fileList.value.findIndex(file => file.name === uploadFile.name && file.type === 'leave')
    if (index !== -1) {
        removeFile(index)
    }
}

// 处理分页变化
const handleCurrentChange = async (page: number, fileIndex: number) => {
    const file = fileList.value[fileIndex]
    file.currentPage = page
    await fetchPageData(fileIndex)
}

const handleSizeChange = async (size: number, fileIndex: number) => {
    const file = fileList.value[fileIndex]
    file.pageSize = size
    file.currentPage = 1
    await fetchPageData(fileIndex)
}

// 获取分页数据
const fetchPageData = async (fileIndex: number) => {
    const file = fileList.value[fileIndex]
    if (!file.preview?.file_id) return

    try {
        const response = await fetch(`/api/data/${file.preview.file_id}?page=${file.currentPage}&size=${file.pageSize}`)
        const result = await response.json()
        if (result.success) {
            file.currentData = result.data.items
            file.headers = result.data.headers
        } else {
            ElMessage.error(result.message || '获取数据失败')
        }
    } catch (error) {
        ElMessage.error('获取数据失败')
    }
}

// 移除文件
const removeFile = async (index: number) => {
    const file = fileList.value[index]
    try {
        const response = await fetch(`/api/file/${file.preview.file_id}`, {
            method: 'DELETE'
        })
        const result = await response.json()
        if (result.success) {
            fileList.value.splice(index, 1)
            ElMessage.success('文件删除成功')
        } else {
            ElMessage.error(result.message || '删除失败')
        }
    } catch (error) {
        console.error('删除文件失败:', error)
        ElMessage.error('删除文件失败')
    }
}

// 上传前验证
const beforeUpload = (file: File) => {
    const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
        file.type === 'application/vnd.ms-excel'
    if (!isExcel) {
        ElMessage.error('只能上传 Excel 文件!')
        return false
    }
    return true
}

// 上传失败处理
const handleUploadError = () => {
    ElMessage.error('文件上传失败')
}

// 格式化数字
const formatNumber = (value: any) => {
    if (value === null || value === undefined) return ''
    if (typeof value === 'number') {
        if (Number.isInteger(value)) {
            return value.toString()
        }
        return value.toFixed(2)
    }
    return value
}

// 格式化日期
const formatDate = (value: any) => {
    if (!value) return ''
    try {
        const date = new Date(value)
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        })
    } catch (e) {
        return value
    }
}

// 导出加班记录
const handleExportOvertime = async () => {
    const overtimeFiles = fileList.value.filter(file => file.type === 'overtime')
    if (overtimeFiles.length === 0) {
        ElMessage.warning('没有可导出的加班记录')
        return
    }

    try {
        const response = await fetch('/api/export/overtime', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_ids: overtimeFiles.map(file => file.preview.file_id)
            })
        })

        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || '导出失败')
        }

        // 获取文件名
        const contentDisposition = response.headers.get('content-disposition')
        let fileName = '加班明细表.xlsx'

        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="([^"]*)"/)
            if (filenameMatch && filenameMatch[1]) {
                try {
                    fileName = decodeURIComponent(filenameMatch[1])
                } catch (e) {
                    console.error('解码文件名失败:', e)
                    fileName = filenameMatch[1]
                }
            }
        }

        // 下载文件
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = fileName
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        ElMessage.success('加班记录导出成功')
    } catch (error) {
        console.error('导出加班记录失败:', error)
        ElMessage.error(error instanceof Error ? error.message : '导出加班记录失败')
    }
}

// 导出请假记录
const handleExportLeave = async () => {
    const leaveFiles = fileList.value.filter(file => file.type === 'leave')
    if (leaveFiles.length === 0) {
        ElMessage.warning('没有可导出的请假记录')
        return
    }

    try {
        const response = await fetch('/api/export/leave', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_ids: leaveFiles.map(file => file.preview.file_id)
            })
        })

        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || '导出失败')
        }

        // 获取文件名
        const contentDisposition = response.headers.get('content-disposition')
        let fileName = '请假明细表.xlsx'

        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="([^"]*)"/)
            if (filenameMatch && filenameMatch[1]) {
                try {
                    fileName = decodeURIComponent(filenameMatch[1])
                } catch (e) {
                    console.error('解码文件名失败:', e)
                    fileName = filenameMatch[1]
                }
            }
        }

        // 下载文件
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = fileName
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        ElMessage.success('请假记录导出成功')
    } catch (error) {
        console.error('导出请假记录失败:', error)
        ElMessage.error(error instanceof Error ? error.message : '导出请假记录失败')
    }
}

// 导出考勤记录
const handleExportAttendance = async () => {
    if (fileList.value.length === 0) {
        ElMessage.warning('没有可导出的考勤记录')
        return
    }

    try {
        const response = await fetch('/api/export/attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_ids: fileList.value.map(file => file.preview.file_id)
            })
        })

        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || '导出失败')
        }

        // 获取文件名
        const contentDisposition = response.headers.get('content-disposition')
        let fileName = `${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}加班统计表.xlsx`

        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="([^"]*)"/)
            if (filenameMatch && filenameMatch[1]) {
                try {
                    fileName = decodeURIComponent(filenameMatch[1])
                } catch (e) {
                    console.error('解码文件名失败:', e)
                }
            }
        }

        // 下载文件
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = fileName
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        ElMessage.success('考勤记录导出成功')
    } catch (error) {
        console.error('导出考勤记录失败:', error)
        ElMessage.error(error instanceof Error ? error.message : '导出考勤记录失败')
    }
}
</script>

<style scoped>
.excel-processor {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.action-buttons {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 16px;
}

:deep(.el-button-group) {
    display: flex;
    gap: 8px;
}

:deep(.el-button-group .el-button) {
    border-radius: 6px !important;
    padding: 8px 16px;
}

:deep(.el-button-group .el-button + .el-button) {
    margin-left: 0;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.file-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.card-header h2 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #1a1a1a;
}

.upload-section {
    display: flex;
    gap: 24px;
}

.upload-card {
    flex: 1;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    border: none;
}

.upload-area {
    width: 100%;
}

:deep(.el-upload-dragger) {
    width: 100%;
    height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 2px dashed var(--el-color-primary-light-3);
}

.upload-icon {
    font-size: 48px;
    color: var(--el-color-primary);
    margin-bottom: 16px;
}

.upload-text {
    text-align: center;
}

.upload-text em {
    color: var(--el-color-primary);
    font-style: normal;
    margin: 0 4px;
}

.upload-tip {
    font-size: 12px;
    color: #64748b;
    margin: 8px 0 0;
}

.preview-card {
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    border: none;
}

.total-count {
    font-size: 14px;
    color: #64748b;
}

.table-wrapper {
    width: 100%;
    margin-bottom: 20px;
}

:deep(.el-table) {
    --el-table-border-color: #e5e7eb;
    --el-table-header-bg-color: #f8fafc;
    --el-table-row-hover-bg-color: #f1f5f9;
}

:deep(.el-table th) {
    background: var(--el-table-header-bg-color);
    font-weight: 600;
    color: #1a1a1a;
}

.pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
    padding: 0 20px;
}

:deep(.el-pagination) {
    --el-pagination-button-bg-color: #ffffff;
    --el-pagination-hover-color: var(--el-color-primary);
    --el-pagination-button-disabled-bg-color: #f8fafc;
}

:deep(.el-pagination .el-select .el-input) {
    width: 120px;
}

.file-tags {
    display: flex;
    align-items: center;
    gap: 12px;
}

:deep(.el-tag--success) {
    --el-tag-bg-color: var(--el-color-success-light-9);
    --el-tag-border-color: var(--el-color-success-light-5);
    --el-tag-text-color: var(--el-color-success);
}

:deep(.el-tag--warning) {
    --el-tag-bg-color: var(--el-color-warning-light-9);
    --el-tag-border-color: var(--el-color-warning-light-5);
    --el-tag-text-color: var(--el-color-warning);
}
</style>