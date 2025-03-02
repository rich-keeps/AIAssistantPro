<template>
    <el-config-provider :locale="locale">
        <div class="excel-processor">
            <!-- 上传区域 -->
            <el-card class="upload-card">
                <template #header>
                    <div class="card-header">
                        <h2>Excel文件上传</h2>
                    </div>
                </template>
                <el-upload class="upload-area" drag action="/api/upload" :on-success="handleUploadSuccess"
                    :on-error="handleUploadError" :before-upload="beforeUpload" accept=".xlsx,.xls">
                    <el-icon class="upload-icon">
                        <Upload />
                    </el-icon>
                    <div class="upload-text">
                        <span>将文件拖到此处或<em>点击上传</em></span>
                        <p class="upload-tip">支持 .xlsx, .xls 格式文件</p>
                    </div>
                </el-upload>
            </el-card>

            <!-- 预览数据 -->
            <el-card v-if="fileInfo.preview" class="preview-card">
                <template #header>
                    <div class="card-header">
                        <h2>数据预览</h2>
                        <span class="total-count">共 {{ fileInfo.preview.total_rows }} 条数据</span>
                    </div>
                </template>
                <div class="table-wrapper">
                    <el-table :data="paginatedData" border>
                        <el-table-column v-for="header in fileInfo.headers" :key="header.key" :prop="header.key"
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
                    <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize"
                        :page-sizes="[10, 20, 50, 100]" :total="fileInfo.preview?.total_rows || 0"
                        layout="total, sizes, prev, pager, next" @size-change="handleSizeChange"
                        @current-change="handleCurrentChange" />
                </div>
            </el-card>
        </div>
    </el-config-provider>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { ExcelPreview, ColumnHeader } from '../types'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const locale = zhCn

const fileInfo = ref({
    preview: null as ExcelPreview | null,
    currentData: [] as any[],
    headers: [] as ColumnHeader[]
})

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(10)

// 计算分页后的数据
const paginatedData = computed(() => {
    return fileInfo.value.currentData || []
})

// 处理分页变化
const handleCurrentChange = async (val: number) => {
    currentPage.value = val
    await fetchPageData()
}

const handleSizeChange = async (val: number) => {
    pageSize.value = val
    currentPage.value = 1
    await fetchPageData()
}

// 获取分页数据
const fetchPageData = async () => {
    if (!fileInfo.value.preview?.file_id) return

    try {
        const response = await fetch(`/api/data/${fileInfo.value.preview.file_id}?page=${currentPage.value}&size=${pageSize.value}`)
        const result = await response.json()
        if (result.success) {
            fileInfo.value.currentData = result.data.items
            fileInfo.value.headers = result.data.headers
        } else {
            ElMessage.error(result.message || '获取数据失败')
        }
    } catch (error) {
        ElMessage.error('获取数据失败')
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

// 上传成功处理
const handleUploadSuccess = async (response: any) => {
    if (response.success) {
        fileInfo.value.preview = response.data
        fileInfo.value.currentData = response.data.sample_data || []
        fileInfo.value.headers = response.data.headers
        currentPage.value = 1
        ElMessage.success('文件上传成功')
    } else {
        ElMessage.error(response.message || '上传失败')
    }
}

// 上传失败处理
const handleUploadError = () => {
    ElMessage.error('文件上传失败')
}

// 格式化数字
const formatNumber = (value: any) => {
    if (value === null || value === undefined) return ''
    if (typeof value === 'number') {
        // 如果是整数，不显示小数点
        if (Number.isInteger(value)) {
            return value.toString()
        }
        // 如果是小数，保留两位小数
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
</script>

<style scoped>
.excel-processor {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card-header h2 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #1a1a1a;
}

.upload-card {
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
</style>