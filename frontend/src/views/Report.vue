<template>
    <div class="report-container">
        <div class="page-header">
            <h2>报表生成</h2>
            <p class="description">在这里您可以生成各类统计报表，包括出差、报销等统计数据</p>
        </div>

        <div class="report-content">
            <el-tabs v-model="activeTab" class="report-tabs">
                <!-- 出差统计 -->
                <el-tab-pane label="出差统计" name="business-trip">
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
                                <el-date-picker v-model="selectedDate" type="month" placeholder="请选择年月"
                                    format="YYYY年MM月" @change="handleMonthChange" />
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
                                <el-button type="primary" @click="handleGenerateBusinessTrip"
                                    :loading="businessTripLoading"
                                    :disabled="!selectedDate || selectedDays.length === 0 || !travelerName.trim()">
                                    {{ businessTripLoading ? '正在生成...' : '生成出差报表' }}
                                </el-button>
                            </el-form-item>
                        </el-form>
                    </el-card>
                </el-tab-pane>

                <!-- 报销统计 -->
                <el-tab-pane label="报销统计" name="expense">
                    <div class="expense-config-card">
                        <div class="expense-config-header">
                            <span>报销统计配置</span>
                        </div>

                        <div class="expense-form">
                            <div class="expense-form-row">
                                <div class="expense-form-item">
                                    <label class="expense-form-label required">填报人</label>
                                    <el-input v-model="expenseName" placeholder="请输入填报人姓名" maxlength="20"
                                        show-word-limit clearable />
                                </div>

                                <div class="expense-form-item">
                                    <label class="expense-form-label required">报销周期</label>
                                    <el-date-picker v-model="expenseMonth" type="month" placeholder="请选择报销周期"
                                        format="YYYY/MM" value-format="YYYY/MM" />
                                </div>
                            </div>
                        </div>

                        <div class="expense-detail-section">
                            <div class="expense-detail-header">报销明细</div>

                            <div class="expense-table">
                                <div class="expense-table-header">
                                    <div class="expense-header-item" style="width: 60px">序号</div>
                                    <div class="expense-header-item" style="width: 120px">日期</div>
                                    <div class="expense-header-item" style="width: 120px">事项</div>
                                    <div class="expense-header-item" style="width: 150px">事由</div>
                                    <div class="expense-header-item" style="width: 120px">发票金额</div>
                                    <div class="expense-header-item" style="width: 180px">发票号</div>
                                    <div class="expense-header-item" style="flex: 1">备注</div>
                                    <div class="expense-header-item" style="width: 140px">操作</div>
                                </div>

                                <div v-for="(item, index) in expenseItems" :key="index" class="expense-item">
                                    <div class="expense-item-cell" style="width: 60px">{{ index + 1 }}</div>
                                    <div class="expense-item-cell" style="width: 120px">
                                        <el-date-picker v-model="item.date" type="date" placeholder="选择日期"
                                            format="YYYY/MM/DD" value-format="YYYY/MM/DD" style="width: 100%" />
                                    </div>
                                    <div class="expense-item-cell" style="width: 120px">
                                        <el-select v-model="item.type" placeholder="选择事项" style="width: 100%">
                                            <el-option label="高速费" value="highway" />
                                            <el-option label="打车费" value="taxi" />
                                            <el-option label="餐饮费" value="meal" />
                                            <el-option label="住宿费" value="accommodation" />
                                            <el-option label="办公用品" value="office" />
                                            <el-option label="其他" value="other" />
                                        </el-select>
                                    </div>
                                    <div class="expense-item-cell" style="width: 150px">
                                        <el-input v-model="item.reason" placeholder="事由" />
                                    </div>
                                    <div class="expense-item-cell" style="width: 120px">
                                        <el-input-number v-model="item.amount" :precision="2" :step="0.01" :min="0"
                                            placeholder="金额" style="width: 100%" controls-position="right" />
                                    </div>
                                    <div class="expense-item-cell" style="width: 180px">
                                        <el-input v-model="item.invoiceNo" placeholder="发票号" />
                                    </div>
                                    <div class="expense-item-cell" style="flex: 1">
                                        <el-input v-model="item.remark" placeholder="备注" />
                                    </div>
                                    <div class="expense-item-cell" style="width: 140px">
                                        <div class="expense-item-actions">
                                            <el-tooltip content="导入发票" placement="top">
                                                <el-icon class="action-icon import-icon" @click="importInvoice(index)">
                                                    <Upload />
                                                </el-icon>
                                            </el-tooltip>
                                            <el-tooltip content="删除" placement="top">
                                                <el-icon class="action-icon delete-icon"
                                                    @click="removeExpenseItem(index)">
                                                    <Delete />
                                                </el-icon>
                                            </el-tooltip>
                                        </div>
                                    </div>
                                </div>

                                <div class="expense-total">
                                    <div class="expense-total-content">
                                        <span>合计金额：</span>
                                        <span class="expense-total-amount">{{ calculateTotalAmount().toFixed(2)
                                        }}</span>
                                    </div>
                                </div>

                                <div class="expense-add-btn">
                                    <el-button type="primary" plain @click="addExpenseItem" class="add-detail-btn">
                                        添加明细
                                    </el-button>
                                </div>
                            </div>
                        </div>

                        <div class="expense-actions">
                            <el-button type="primary" @click="handleGenerateExpense" :loading="expenseLoading"
                                :disabled="!expenseName.trim() || !expenseMonth || expenseItems.length === 0"
                                class="generate-btn">
                                {{ expenseLoading ? '正在生成...' : '生成报销报表' }}
                            </el-button>
                        </div>
                    </div>
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Delete } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import { reportApi } from '@/api/report'
import { downloadFile, getMonthDays } from '@/utils/common'
import axios from 'axios'

dayjs.locale('zh-cn')

// 当前激活的标签页
const activeTab = ref('business-trip')

// 出差统计状态
const travelerName = ref('')
const selectedDate = ref<Date | null>(null)
const daysInMonth = ref<Array<{ date: string; label: string; isWorkday: boolean }>>([])
const selectedDays = ref<string[]>([])
const checkAll = ref(false)
const businessTripLoading = ref(false)

// 报销统计状态
const expenseName = ref('')
const expenseMonth = ref('')
const expenseItems = ref<Array<{
    date: string;
    type: string;
    reason: string;
    amount: number;
    invoiceNo: string;
    remark: string;
}>>([])
const expenseLoading = ref(false)

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

// 生成出差报表
const handleGenerateBusinessTrip = async () => {
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
        businessTripLoading.value = true

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

        ElMessage.success('出差报表生成成功')
    } catch (error) {
        console.error('生成出差报表失败:', error)
        ElMessage.error('生成出差报表失败，请重试')
    } finally {
        businessTripLoading.value = false
    }
}

// 添加报销明细项
const addExpenseItem = () => {
    expenseItems.value.push({
        date: dayjs().format('YYYY/MM/DD'),
        type: '',
        reason: '',
        amount: 0,
        invoiceNo: '',
        remark: ''
    })
}

// 移除报销明细项
const removeExpenseItem = (index: number) => {
    expenseItems.value.splice(index, 1)
}

// 导入发票
const importInvoice = async (index: number) => {
    try {
        // 创建文件选择器
        const input = document.createElement('input')
        input.type = 'file'
        input.accept = 'image/jpeg,image/png,image/jpg,application/pdf'

        // 监听文件选择事件
        input.onchange = async (event) => {
            const target = event.target as HTMLInputElement
            const file = target.files?.[0]

            if (!file) {
                ElMessage.warning('请选择发票文件')
                return
            }

            // 文件大小限制（10MB）
            if (file.size > 10 * 1024 * 1024) {
                ElMessage.warning('文件大小不能超过10MB')
                return
            }

            // 显示上传中提示
            ElMessage.info('正在上传并识别发票...')

            // 创建FormData对象
            const formData = new FormData()
            formData.append('file', file)
            formData.append('type', 'invoice')

            try {
                // 调用上传API
                const response = await axios.post('/api/invoice/upload', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                })

                // 处理响应
                if (response.data.success) {
                    const invoiceData = response.data.data

                    // 更新明细项
                    if (invoiceData) {
                        // 根据发票类型设置事项
                        const typeMap: Record<string, string> = {
                            'highway': 'highway',  // 高速费
                            'taxi': 'taxi',        // 打车费
                            'meal': 'meal',        // 餐饮费
                            'accommodation': 'accommodation', // 住宿费
                            'office': 'office',    // 办公用品
                            'other': 'other'       // 其他
                        }

                        // 更新明细项数据
                        expenseItems.value[index].amount = invoiceData.amount || expenseItems.value[index].amount
                        expenseItems.value[index].invoiceNo = invoiceData.invoice_no || expenseItems.value[index].invoiceNo

                        // 如果识别出发票类型，则更新类型
                        if (invoiceData.type && typeMap[invoiceData.type]) {
                            expenseItems.value[index].type = typeMap[invoiceData.type]
                        }

                        ElMessage.success('发票导入成功')
                    } else {
                        ElMessage.warning('发票识别结果为空，请手动填写')
                    }
                } else {
                    ElMessage.error(response.data.message || '发票识别失败')
                }
            } catch (error) {
                console.error('发票上传失败:', error)
                ElMessage.error('发票上传失败，请重试')
            }
        }

        // 触发文件选择器
        input.click()
    } catch (error) {
        console.error('导入发票失败:', error)
        ElMessage.error('导入发票失败，请重试')
    }
}

// 计算报销总金额
const calculateTotalAmount = () => {
    return expenseItems.value.reduce((total, item) => total + (item.amount || 0), 0)
}

// 生成报销报表
const handleGenerateExpense = async () => {
    if (!expenseName.value.trim()) {
        ElMessage.warning('请输入填报人姓名')
        return
    }
    if (!expenseMonth.value) {
        ElMessage.warning('请选择报销周期')
        return
    }
    if (expenseItems.value.length === 0) {
        ElMessage.warning('请至少添加一条报销明细')
        return
    }

    // 验证每条明细是否完整
    for (let i = 0; i < expenseItems.value.length; i++) {
        const item = expenseItems.value[i]
        if (!item.date) {
            ElMessage.warning(`第${i + 1}条明细的日期不能为空`)
            return
        }
        if (!item.type) {
            ElMessage.warning(`第${i + 1}条明细的事项不能为空`)
            return
        }
        if (!item.invoiceNo) {
            ElMessage.warning(`第${i + 1}条明细的发票号不能为空`)
            return
        }
        if (!item.amount) {
            ElMessage.warning(`第${i + 1}条明细的金额不能为0`)
            return
        }
    }

    try {
        expenseLoading.value = true

        // 准备请求参数
        const params = {
            name: expenseName.value.trim(),
            month: expenseMonth.value,
            expense_items: expenseItems.value.map(item => ({
                date: item.date,
                type: item.type,
                reason: item.reason,
                amount: item.amount,
                invoice_no: item.invoiceNo || '',
                remark: item.remark || ''
            }))
        }

        // 调用报销明细表生成API
        const response = await reportApi.generateExpenseReport(params)

        // 下载文件
        downloadFile(
            response.data,
            `${params.month.replace('/', '')}${params.name}报销明细.xlsx`
        )

        ElMessage.success('报销明细表生成成功')
    } catch (error) {
        console.error('生成报销明细表失败:', error)
        ElMessage.error('生成报销明细表失败，请重试')
    } finally {
        expenseLoading.value = false
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
    max-width: 100%;
}

.report-tabs {
    background: #ffffff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.report-card {
    margin-bottom: 16px;
    width: 100%;
    box-shadow: none;
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

:deep(.el-select) {
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

:deep(.el-tabs__nav-wrap::after) {
    height: 1px;
    background-color: #e5e7eb;
}

:deep(.el-tabs__item) {
    font-size: 14px;
    color: #64748b;
}

:deep(.el-tabs__item.is-active) {
    color: var(--el-color-primary);
    font-weight: 500;
}

/* 报销统计样式 */
.expense-config-card {
    background-color: #fff;
    border-radius: 4px;
    overflow: hidden;
    width: 100%;
}

.expense-config-header {
    padding: 16px 20px;
    font-size: 16px;
    font-weight: 500;
    color: #333;
    border-bottom: 1px solid #f0f0f0;
}

.expense-form {
    padding: 20px;
    border-bottom: 1px solid #f0f0f0;
}

.expense-form-row {
    display: flex;
    gap: 40px;
}

.expense-form-item {
    display: flex;
    flex-direction: column;
    position: relative;
    margin-bottom: 16px;
    width: 360px;
}

.expense-form-label {
    font-size: 14px;
    color: #606266;
    margin-bottom: 8px;
}

.expense-form-label.required::before {
    content: '*';
    color: #f56c6c;
    margin-right: 4px;
}

.expense-detail-section {
    padding: 0 20px;
}

.expense-detail-header {
    font-size: 14px;
    font-weight: 500;
    color: #606266;
    margin: 16px 0;
    padding-left: 8px;
    border-left: 3px solid #67c23a;
}

.expense-table {
    border: 1px solid #ebeef5;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 20px;
    width: 100%;
}

.expense-table-header {
    display: flex;
    background-color: #f5f7fa;
    padding: 12px 0;
    border-bottom: 1px solid #ebeef5;
}

.expense-header-item {
    font-weight: 500;
    color: #606266;
    font-size: 14px;
    padding: 0 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.expense-item {
    display: flex;
    border-bottom: 1px solid #ebeef5;
    padding: 10px 0;
    background-color: #fff;
}

.expense-item:last-child {
    border-bottom: none;
}

.expense-item-cell {
    padding: 0 5px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.expense-item-actions {
    display: flex;
    gap: 16px;
    align-items: center;
}

.action-icon {
    cursor: pointer;
    font-size: 20px;
    color: #909399;
    transition: color 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
}

.import-icon:hover {
    color: #409eff;
}

.delete-icon:hover {
    color: #f56c6c;
}

.expense-total {
    display: flex;
    justify-content: flex-end;
    padding: 12px 20px;
    background-color: #f5f7fa;
    border-top: 1px solid #ebeef5;
}

.expense-total-content {
    font-size: 14px;
    color: #606266;
}

.expense-total-amount {
    font-weight: 600;
    color: #f56c6c;
    margin-left: 8px;
}

.expense-add-btn {
    padding: 16px 0;
    display: flex;
    justify-content: center;
    border-top: 1px solid #ebeef5;
    background-color: #fff;
}

.add-detail-btn {
    width: 120px;
}

.expense-actions {
    padding: 20px;
    display: flex;
    justify-content: center;
}

.generate-btn {
    width: 140px;
}

:deep(.el-input-number .el-input__inner) {
    text-align: left;
}
</style>