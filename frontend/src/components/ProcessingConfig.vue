<template>
  <div class="processing-config">
    <el-form :model="config" label-width="120px">
      <!-- 列映射配置 -->
      <el-card class="config-card">
        <template #header>
          <div class="card-header">
            <span>列映射配置</span>
            <el-button type="primary" @click="addColumnMapping">添加映射</el-button>
          </div>
        </template>
        <div v-for="(mapping, index) in config.column_mappings" :key="index" class="mapping-item">
          <el-form-item :label="'映射 ' + (index + 1)">
            <el-row :gutter="10">
              <el-col :span="8">
                <el-select v-model="mapping.source" placeholder="源列名">
                  <el-option
                    v-for="header in headers"
                    :key="header"
                    :label="header"
                    :value="header"
                  />
                </el-select>
              </el-col>
              <el-col :span="8">
                <el-input v-model="mapping.target" placeholder="目标列名" />
              </el-col>
              <el-col :span="6">
                <el-select v-model="mapping.type" placeholder="数据类型">
                  <el-option label="文本" value="text" />
                  <el-option label="数字" value="number" />
                  <el-option label="日期" value="date" />
                </el-select>
              </el-col>
              <el-col :span="2">
                <el-button type="danger" @click="removeColumnMapping(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-col>
            </el-row>
          </el-form-item>
        </div>
      </el-card>

      <!-- 格式化配置 -->
      <el-card class="config-card">
        <template #header>
          <div class="card-header">
            <span>格式化配置</span>
          </div>
        </template>
        <el-form-item label="日期列">
          <el-select
            v-model="config.date_columns"
            multiple
            placeholder="选择需要格式化的日期列"
          >
            <el-option
              v-for="header in headers"
              :key="header"
              :label="header"
              :value="header"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="数字列">
          <el-select
            v-model="config.numeric_columns"
            multiple
            placeholder="选择需要格式化的数字列"
          >
            <el-option
              v-for="header in headers"
              :key="header"
              :label="header"
              :value="header"
            />
          </el-select>
        </el-form-item>
      </el-card>

      <!-- 分类配置 -->
      <el-card class="config-card">
        <template #header>
          <div class="card-header">
            <span>分类配置</span>
          </div>
        </template>
        <el-form-item label="分类列">
          <el-select
            v-model="config.category_column"
            clearable
            placeholder="选择用于分类的列"
          >
            <el-option
              v-for="header in headers"
              :key="header"
              :label="header"
              :value="header"
            />
          </el-select>
        </el-form-item>
      </el-card>

      <!-- 过滤条件 -->
      <el-card class="config-card">
        <template #header>
          <div class="card-header">
            <span>过滤条件</span>
            <el-button type="primary" @click="addFilter">添加条件</el-button>
          </div>
        </template>
        <div v-for="(filter, index) in config.filters" :key="index" class="filter-item">
          <el-form-item :label="'条件 ' + (index + 1)">
            <el-row :gutter="10">
              <el-col :span="8">
                <el-select v-model="filter.column" placeholder="选择列">
                  <el-option
                    v-for="header in headers"
                    :key="header"
                    :label="header"
                    :value="header"
                  />
                </el-select>
              </el-col>
              <el-col :span="6">
                <el-select v-model="filter.operator" placeholder="操作符">
                  <el-option label="等于" value="eq" />
                  <el-option label="大于" value="gt" />
                  <el-option label="小于" value="lt" />
                  <el-option label="包含" value="contains" />
                </el-select>
              </el-col>
              <el-col :span="8">
                <el-input v-model="filter.value" placeholder="过滤值" />
              </el-col>
              <el-col :span="2">
                <el-button type="danger" @click="removeFilter(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-col>
            </el-row>
          </el-form-item>
        </div>
      </el-card>

      <!-- 提交按钮 -->
      <div class="submit-buttons">
        <el-button type="primary" @click="submitConfig">开始处理</el-button>
        <el-button @click="resetConfig">重置配置</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import type { ColumnMapping, FilterCondition } from '../types'

const props = defineProps<{
  headers: string[]
}>()

const emit = defineEmits<{
  (e: 'submit', config: any): void
}>()

const defaultConfig = {
  column_mappings: [] as ColumnMapping[],
  date_columns: [] as string[],
  numeric_columns: [] as string[],
  category_column: '',
  filters: [] as FilterCondition[]
}

const config = ref({ ...defaultConfig })

const addColumnMapping = () => {
  config.value.column_mappings.push({
    source: '',
    target: '',
    type: 'text'
  })
}

const removeColumnMapping = (index: number) => {
  config.value.column_mappings.splice(index, 1)
}

const addFilter = () => {
  config.value.filters.push({
    column: '',
    operator: 'eq',
    value: ''
  })
}

const removeFilter = (index: number) => {
  config.value.filters.splice(index, 1)
}

const submitConfig = () => {
  emit('submit', config.value)
}

const resetConfig = () => {
  config.value = { ...defaultConfig }
}
</script>

<style scoped>
.processing-config {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.config-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mapping-item,
.filter-item {
  margin-bottom: 10px;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.submit-buttons {
  margin-top: 20px;
  text-align: center;
}

:deep(.el-form-item__content) {
  flex-wrap: nowrap;
}
</style> 