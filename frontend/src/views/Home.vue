<template>
  <div class="home">
    <!-- 上传卡片 -->
    <el-card v-if="!filePreview" class="upload-card">
      <el-upload
        class="upload-area"
        drag
        action="/api/upload"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
        :disabled="uploading"
        accept=".xlsx,.xls"
      >
        <template v-if="!uploading">
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或 <em>点击上传</em>
          </div>
        </template>
        <template v-else>
          <el-icon class="el-icon--loading"><loading /></el-icon>
          <div class="el-upload__text">
            正在上传文件...
          </div>
        </template>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 xlsx/xls 文件
          </div>
        </template>
      </el-upload>
    </el-card>

    <!-- 预览和配置区域 -->
    <template v-else>
      <!-- 预览卡片 -->
      <el-card class="preview-card">
        <template #header>
          <div class="card-header">
            <span>数据预览</span>
            <el-button @click="resetUpload">重新上传</el-button>
          </div>
        </template>
        <el-table :data="filePreview.sample_data" border style="width: 100%">
          <el-table-column
            v-for="header in filePreview.headers"
            :key="header"
            :prop="header"
            :label="header"
          />
        </el-table>
        <div class="preview-info">
          总行数: {{ filePreview.total_rows }}
        </div>
      </el-card>

      <!-- 配置组件 -->
      <processing-config
        :headers="filePreview.headers"
        @submit="handleConfigSubmit"
      />
    </template>

    <!-- 处理结果 -->
    <el-dialog
      v-model="showResult"
      title="处理结果"
      width="50%"
    >
      <div v-if="processingResult">
        <div class="result-stats">
          <h3>统计信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="总行数">
              {{ processingResult.stats.total_rows }}
            </el-descriptions-item>
            <el-descriptions-item label="总列数">
              {{ processingResult.stats.total_columns }}
            </el-descriptions-item>
          </el-descriptions>
          
          <h4>列类型</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item
              v-for="(type, col) in processingResult.stats.column_types"
              :key="col"
              :label="col"
            >
              {{ type }}
            </el-descriptions-item>
          </el-descriptions>

          <template v-if="processingResult.stats.categories">
            <h4>分类统计</h4>
            <el-descriptions :column="2" border>
              <el-descriptions-item
                v-for="(count, category) in processingResult.stats.categories"
                :key="category"
                :label="category"
              >
                {{ count }}
              </el-descriptions-item>
            </el-descriptions>
          </template>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="downloadFile">
            下载处理后的文件
          </el-button>
          <el-button @click="showResult = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UploadFilled, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ProcessingConfig from '../components/ProcessingConfig.vue'
import type { ExcelPreview, ProcessingConfig as IProcessingConfig } from '../types'

const filePreview = ref<ExcelPreview | null>(null)
const showResult = ref(false)
const processingResult = ref<any>(null)
const uploading = ref(false)
const processing = ref(false)

const beforeUpload = (file: File) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                  file.type === 'application/vnd.ms-excel'
  if (!isExcel) {
    ElMessage.error('只能上传 Excel 文件!')
    return false
  }
  uploading.value = true
  return true
}

const handleUploadSuccess = (response: any) => {
  uploading.value = false
  if (response.success) {
    filePreview.value = response.data
    ElMessage.success('文件上传成功')
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

const handleUploadError = (error: any) => {
  uploading.value = false
  ElMessage.error('文件上传失败: ' + error.message)
}

const resetUpload = () => {
  if (uploading.value || processing.value) return
  filePreview.value = null
  processingResult.value = null
  showResult.value = false
}

const handleConfigSubmit = async (config: IProcessingConfig) => {
  if (!filePreview.value?.file_id) {
    ElMessage.error('文件不存在')
    return
  }

  processing.value = true
  try {
    const response = await fetch(`/api/process/${filePreview.value.file_id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config)
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    if (result.success) {
      processingResult.value = result.data
      showResult.value = true
      ElMessage.success('处理成功')
    } else {
      throw new Error(result.message || '处理失败')
    }
  } catch (error) {
    console.error('处理失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '处理请求失败')
  } finally {
    processing.value = false
  }
}

const downloadFile = async () => {
  if (!filePreview.value?.file_id) {
    ElMessage.error('文件不存在')
    return
  }

  try {
    const response = await fetch(`/api/download/${filePreview.value.file_id}`)
    if (!response.ok) {
      throw new Error('下载失败')
    }

    const contentDisposition = response.headers.get('content-disposition')
    let filename = `processed_${filePreview.value.file_id}.xlsx`
    if (contentDisposition) {
      const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition)
      if (matches != null && matches[1]) {
        filename = matches[1].replace(/['"]/g, '')
      }
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '下载失败')
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.upload-card {
  margin-bottom: 20px;
}

.upload-area {
  width: 100%;
}

.preview-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-info {
  margin-top: 20px;
  text-align: right;
  color: #666;
}

.result-stats {
  h3, h4 {
    margin-top: 20px;
    margin-bottom: 10px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 