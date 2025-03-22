<template>
    <el-config-provider :locale="locale">
        <div class="excel-processor">
            <!-- 功能按钮区域 -->
            <div class="action-buttons">
                <el-button-group>
                    <el-button type="success" :icon="Download" @click="handleExportOvertime"
                        :disabled="!hasOvertimeFile">
                        导出加班记录
                    </el-button>
                    <el-button type="warning" :icon="Download" @click="handleExportLeave" :disabled="!hasLeaveFile">
                        导出请假记录
                    </el-button>
                    <el-button type="primary" :icon="Download" @click="handleExportAttendance" :disabled="!hasAnyFile">
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
                    <el-upload class="upload-area" drag :action="API_ENDPOINTS.UPLOAD + '?type=overtime'"
                        :on-success="handleOvertimeUploadSuccess" :on-error="handleUploadError"
                        :before-upload="beforeUpload" accept=".xlsx,.xls" ref="overtimeUploadRef"
                        :on-remove="handleOvertimeUploadRemove" :file-list="overtimeFileList">
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
                    <el-upload class="upload-area" drag :action="API_ENDPOINTS.UPLOAD + '?type=leave'"
                        :on-success="handleLeaveUploadSuccess" :on-error="handleUploadError"
                        :before-upload="beforeUpload" accept=".xlsx,.xls" ref="leaveUploadRef"
                        :on-remove="handleLeaveUploadRemove" :file-list="leaveFileList">
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
                                    <span v-if="header.type === 'number'">
                                        {{ formatNumber(scope.row[header.key]) }}
                                    </span>
                                    <span v-else-if="header.type === 'datetime'">
                                        {{ formatDate(scope.row[header.key]) }}
                                    </span>
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
import type { UploadInstance, UploadFile } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { attendanceApi } from '@/api/attendance'
import type { FileInfo } from '@/types'
import { downloadFile, getFilenameFromHeaders } from '@/utils/common'
import { API_ENDPOINTS } from '@/config'

const locale = zhCn
const overtimeUploadRef = ref<UploadInstance>()
const leaveUploadRef = ref<UploadInstance>()

// 文件列表
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

// 计算属性：是否有加班文件
const hasOvertimeFile = computed(() => fileList.value.some(file => file.type === 'overtime'))

// 计算属性：是否有请假文件
const hasLeaveFile = computed(() => fileList.value.some(file => file.type === 'leave'))

// 计算属性：是否有任何文件
const hasAnyFile = computed(() => fileList.value.length > 0)

// 处理加班记录上传成功
const handleOvertimeUploadSuccess = async (response: any, uploadFile: UploadFile) => {
    if (response.success) {
        // 移除之前的加班记录
        const overtimeIndex = fileList.value.findIndex(file => file.type === 'overtime')
        if (overtimeIndex !== -1) {
            await removeFile(overtimeIndex)
        }

        // 过滤掉表头数据
        const filteredData = {
            ...response.data,
            sample_data: response.data.sample_data.filter((row: any) =>
                row['加班人'] !== '加班人' &&
                row['开始时间'] !== '开始时间' &&
                row['结束时间'] !== '结束时间'
            )
        }

        const newFile: FileInfo = {
            id: response.data.file_id,
            name: uploadFile.name,
            type: 'overtime',
            preview: filteredData,
            currentData: filteredData.sample_data || [],
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
const handleLeaveUploadSuccess = async (response: any, uploadFile: UploadFile) => {
    if (response.success) {
        // 移除之前的请假记录
        const leaveIndex = fileList.value.findIndex(file => file.type === 'leave')
        if (leaveIndex !== -1) {
            await removeFile(leaveIndex)
        }

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

// 处理分页大小变化
const handleSizeChange = (size: number, index: number) => {
    const file = fileList.value[index]
    file.pageSize = size
    updateCurrentData(index)
}

// 处理页码变化
const handleCurrentChange = (page: number, index: number) => {
    const file = fileList.value[index]
    file.currentPage = page
    updateCurrentData(index)
}

// 更新当前显示的数据
const updateCurrentData = (index: number) => {
    const file = fileList.value[index]
    const start = (file.currentPage - 1) * file.pageSize
    const end = start + file.pageSize
    file.currentData = file.preview.sample_data.slice(start, end)
}

// 移除文件
const removeFile = async (index: number) => {
    const file = fileList.value[index]
    try {
        await attendanceApi.deleteFile(file.preview.file_id)
        fileList.value.splice(index, 1)
        ElMessage.success('文件已移除')
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
    const overtimeFile = fileList.value.find(file => file.type === 'overtime')
    if (!overtimeFile) {
        ElMessage.warning('请先上传加班记录')
        return
    }

    try {
        const response = await attendanceApi.exportOvertime(overtimeFile.preview.file_id)

        // 尝试从响应头中获取文件名
        const headerFilename = getFilenameFromHeaders(response.headers)

        // 如果响应头中有文件名，则使用它，否则使用前端生成的文件名
        let filename
        if (headerFilename) {
            filename = headerFilename
        } else {
            // 获取当前日期并格式化为年月日
            const today = new Date()
            const year = today.getFullYear()
            const month = String(today.getMonth() + 1).padStart(2, '0')
            const day = String(today.getDate()).padStart(2, '0')
            const dateStr = `${year}${month}${day}`
            filename = `${dateStr}加班记录.xlsx`
        }

        downloadFile(response.data, filename)
        ElMessage.success('导出成功')
    } catch (error) {
        console.error('导出失败:', error)
        ElMessage.error('导出失败，请重试')
    }
}

// 导出请假记录
const handleExportLeave = async () => {
    const leaveFile = fileList.value.find(file => file.type === 'leave')
    if (!leaveFile) {
        ElMessage.warning('请先上传请假记录')
        return
    }

    try {
        const response = await attendanceApi.exportLeave(leaveFile.preview.file_id)

        // 尝试从响应头中获取文件名
        const headerFilename = getFilenameFromHeaders(response.headers)

        // 如果响应头中有文件名，则使用它，否则使用前端生成的文件名
        let filename
        if (headerFilename) {
            filename = headerFilename
        } else {
            // 获取当前日期并格式化为年月日
            const today = new Date()
            const year = today.getFullYear()
            const month = String(today.getMonth() + 1).padStart(2, '0')
            const day = String(today.getDate()).padStart(2, '0')
            const dateStr = `${year}${month}${day}`
            filename = `${dateStr}请假记录.xlsx`
        }

        downloadFile(response.data, filename)
        ElMessage.success('导出成功')
    } catch (error) {
        console.error('导出失败:', error)
        ElMessage.error('导出失败，请重试')
    }
}

// 导出考勤记录
const handleExportAttendance = async () => {
    if (fileList.value.length === 0) {
        ElMessage.warning('请先上传文件')
        return
    }

    try {
        // 获取所有文件的ID
        const fileIds = fileList.value.map(file => file.preview.file_id)
        const response = await attendanceApi.exportAttendance(fileIds)

        // 尝试从响应头中获取文件名
        const headerFilename = getFilenameFromHeaders(response.headers)

        // 如果响应头中有文件名，则使用它，否则使用前端生成的文件名
        let filename
        if (headerFilename) {
            filename = headerFilename
        } else {
            // 获取当前日期并格式化为年月日
            const today = new Date()
            const year = today.getFullYear()
            const month = String(today.getMonth() + 1).padStart(2, '0')
            const day = String(today.getDate()).padStart(2, '0')
            const dateStr = `${year}${month}${day}`
            filename = `${dateStr}考勤记录.xlsx`
        }

        downloadFile(response.data, filename)
        ElMessage.success('导出成功')
    } catch (error) {
        console.error('导出失败:', error)
        ElMessage.error('导出失败，请重试')
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