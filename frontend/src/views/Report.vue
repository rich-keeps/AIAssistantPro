<template>
    <div class="report-container">
        <div class="page-header">
            <h2>出差统计</h2>
            <p class="description">在这里您可以生成各类出差统计报表，包括出差天数、费用等统计数据</p>
        </div>

        <div class="report-content">
            <el-card class="report-card">
                <template #header>
                    <div class="card-header">
                        <span>出差统计配置</span>
                    </div>
                </template>

                <el-form label-width="90px">
                    <el-form-item label="出差人" required>
                        <el-input v-model="travelerName" placeholder="请输入出差人姓名" maxlength="20" show-word-limit
                            clearable />
                    </el-form-item>

                    <el-form-item label="选择年月">
                        <el-date-picker v-model="selectedDate" type="month" placeholder="请选择年月" format="YYYY年MM月"
                            @change="handleMonthChange" />
                    </el-form-item>

                    <el-form-item label="选择日期" v-if="daysInMonth.length > 0">
                        <div class="days-checkbox-group">
                            <el-checkbox v-model="checkAll" @change="handleCheckAllChange">全选</el-checkbox>
                            <el-divider />
                            <el-checkbox-group v-model="selectedDays" @change="handleCheckedDaysChange">
                                <el-checkbox v-for="day in daysInMonth" :key="day.date" :label="day.date"
                                    :class="{ 'is-workday': day.isWorkday }">
                                    {{ day.label }}
                                </el-checkbox>
                            </el-checkbox-group>
                        </div>
                    </el-form-item>

                    <el-form-item>
                        <el-button type="primary" @click="handleGenerate" :loading="loading"
                            :disabled="!selectedDate || selectedDays.length === 0 || !travelerName.trim()">
                            {{ loading ? '正在生成...' : '生成统计报表' }}
                        </el-button>
                    </el-form-item>
                </el-form>
            </el-card>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import { reportApi } from '@/api/report'
import { downloadFile, getMonthDays } from '@/utils/common'

dayjs.locale('zh-cn')

// 状态定义
const travelerName = ref('')
const selectedDate = ref<Date | null>(null)
const daysInMonth = ref<Array<{ date: string; label: string; isWorkday: boolean }>>([])
const selectedDays = ref<string[]>([])
const checkAll = ref(false)
const loading = ref(false)

// 监听月份变化
const handleMonthChange = async (date: Date | null) => {
    if (!date) {
        daysInMonth.value = []
        selectedDays.value = []
        return
    }

    const year = date.getFullYear()
    const month = date.getMonth() + 1

    try {
        // 获取该月的所有日期（异步）
        daysInMonth.value = await getMonthDays(year, month)

        // 默认选中工作日
        selectedDays.value = daysInMonth.value
            .filter(day => day.isWorkday)
            .map(day => day.date)

        // 更新全选状态
        updateCheckAllStatus()
    } catch (error) {
        console.error('获取月份日期失败:', error)
        ElMessage.error('获取日期数据失败，请重试')
    }
}

// 处理全选变化
const handleCheckAllChange = (val: boolean) => {
    selectedDays.value = val ? daysInMonth.value.map(day => day.date) : []
}

// 处理选中日期变化
const handleCheckedDaysChange = (value: string[]) => {
    const checkedCount = value.length
    checkAll.value = checkedCount === daysInMonth.value.length
}

// 更新全选状态
const updateCheckAllStatus = () => {
    checkAll.value = selectedDays.value.length === daysInMonth.value.length
}

// 生成报表
const handleGenerate = async () => {
    if (!travelerName.value.trim()) {
        ElMessage.warning('请输入出差人姓名')
        return
    }
    if (!selectedDate.value) {
        ElMessage.warning('请选择年月')
        return
    }
    if (selectedDays.value.length === 0) {
        ElMessage.warning('请至少选择一天')
        return
    }

    try {
        loading.value = true

        // 准备请求参数
        const params = {
            name: travelerName.value.trim(),
            month: dayjs(selectedDate.value).format('YYYY-MM'),
            dates: selectedDays.value
        }

        // 发送请求获取Excel文件
        const response = await reportApi.generateReport(params)

        // 下载文件
        downloadFile(
            response.data,
            `${params.name}-${params.month}出差统计表.xlsx`
        )

        ElMessage.success('报表生成成功')
    } catch (error) {
        console.error('生成报表失败:', error)
        ElMessage.error('生成报表失败，请重试')
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.report-container {
    padding: 16px;
}

.page-header {
    margin-bottom: 16px;
}

.page-header h2 {
    margin: 0;
    font-size: 20px;
    color: #1a1a1a;
}

.description {
    margin: 4px 0 0;
    color: #64748b;
    font-size: 14px;
}

.report-content {
    width: 100%;
    max-width: 1000px;
}

.report-card {
    margin-bottom: 16px;
    width: 100%;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
}

.el-form {
    width: 100%;
    padding: 16px 0;
}

.days-checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: 100%;
    padding: 0 8px;
}


.el-checkbox-group {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px;
    width: 100%;
}

.el-checkbox {
    margin: 0 !important;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    border-radius: 4px;
    transition: background-color 0.3s;
    font-size: 13px;
}

.el-checkbox:hover {
    background-color: var(--el-fill-color-light);
}

.is-workday {
    color: var(--el-color-primary);
}

.el-divider {
    margin: 8px 0;
    width: 100%;
}

:deep(.el-form-item) {
    margin-bottom: 16px;
}

:deep(.el-form-item__content) {
    width: calc(100% - 120px);
}

:deep(.el-date-editor) {
    width: 100%;
    max-width: 300px;
}

:deep(.el-input) {
    width: 100%;
    max-width: 300px;
}

:deep(.el-checkbox__label) {
    padding-left: 6px;
}
</style>