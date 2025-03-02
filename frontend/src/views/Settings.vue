<template>
    <div class="settings-container">
        <div class="page-header">
            <h1>系统设置</h1>
            <div class="header-actions">
                <el-button type="primary" @click="handleSave">保存设置</el-button>
            </div>
        </div>

        <el-tabs v-model="activeTab" class="settings-tabs">
            <!-- 基本设置 -->
            <el-tab-pane label="基本设置" name="basic">
                <el-form :model="basicSettings" label-width="120px">
                    <el-form-item label="系统名称">
                        <el-input v-model="basicSettings.systemName" placeholder="请输入系统名称" />
                    </el-form-item>
                    <el-form-item label="公司名称">
                        <el-input v-model="basicSettings.companyName" placeholder="请输入公司名称" />
                    </el-form-item>
                    <el-form-item label="工作时间">
                        <el-time-picker v-model="basicSettings.workStartTime" placeholder="上班时间" format="HH:mm" />
                        <span class="separator">至</span>
                        <el-time-picker v-model="basicSettings.workEndTime" placeholder="下班时间" format="HH:mm" />
                    </el-form-item>
                    <el-form-item label="工作日">
                        <el-checkbox-group v-model="basicSettings.workDays">
                            <el-checkbox label="1">周一</el-checkbox>
                            <el-checkbox label="2">周二</el-checkbox>
                            <el-checkbox label="3">周三</el-checkbox>
                            <el-checkbox label="4">周四</el-checkbox>
                            <el-checkbox label="5">周五</el-checkbox>
                            <el-checkbox label="6">周六</el-checkbox>
                            <el-checkbox label="7">周日</el-checkbox>
                        </el-checkbox-group>
                    </el-form-item>
                </el-form>
            </el-tab-pane>

            <!-- 考勤规则 -->
            <el-tab-pane label="考勤规则" name="rules">
                <el-form :model="attendanceRules" label-width="120px">
                    <el-form-item label="迟到规则">
                        <el-input-number v-model="attendanceRules.lateThreshold" :min="0" :max="60"
                            placeholder="迟到阈值(分钟)" />
                        <span class="rule-hint">超过上班时间多少分钟算作迟到</span>
                    </el-form-item>
                    <el-form-item label="早退规则">
                        <el-input-number v-model="attendanceRules.earlyLeaveThreshold" :min="0" :max="60"
                            placeholder="早退阈值(分钟)" />
                        <span class="rule-hint">早于下班时间多少分钟算作早退</span>
                    </el-form-item>
                    <el-form-item label="加班规则">
                        <el-input-number v-model="attendanceRules.overtimeThreshold" :min="0" :max="60"
                            placeholder="加班阈值(分钟)" />
                        <span class="rule-hint">超过下班时间多少分钟开始计算加班</span>
                    </el-form-item>
                    <el-form-item label="特殊日期">
                        <el-button type="primary" plain @click="handleAddSpecialDate">
                            添加特殊日期
                        </el-button>
                        <div class="special-dates">
                            <el-tag v-for="date in attendanceRules.specialDates" :key="date" closable
                                @close="handleRemoveDate(date)">
                                {{ date }}
                            </el-tag>
                        </div>
                    </el-form-item>
                </el-form>
            </el-tab-pane>

            <!-- 通知设置 -->
            <el-tab-pane label="通知设置" name="notifications">
                <el-form :model="notificationSettings" label-width="120px">
                    <el-form-item label="邮件通知">
                        <el-switch v-model="notificationSettings.emailEnabled" />
                    </el-form-item>
                    <el-form-item label="通知事件">
                        <el-checkbox-group v-model="notificationSettings.events">
                            <el-checkbox label="late">迟到提醒</el-checkbox>
                            <el-checkbox label="absent">缺勤提醒</el-checkbox>
                            <el-checkbox label="overtime">加班提醒</el-checkbox>
                            <el-checkbox label="leave">请假审批</el-checkbox>
                        </el-checkbox-group>
                    </el-form-item>
                    <el-form-item label="SMTP服务器" v-if="notificationSettings.emailEnabled">
                        <el-input v-model="notificationSettings.smtpServer" placeholder="SMTP服务器地址" />
                    </el-form-item>
                    <el-form-item label="SMTP端口" v-if="notificationSettings.emailEnabled">
                        <el-input-number v-model="notificationSettings.smtpPort" :min="1" :max="65535" />
                    </el-form-item>
                    <el-form-item label="发件邮箱" v-if="notificationSettings.emailEnabled">
                        <el-input v-model="notificationSettings.senderEmail" placeholder="发件人邮箱地址" />
                    </el-form-item>
                    <el-form-item label="邮箱密码" v-if="notificationSettings.emailEnabled">
                        <el-input v-model="notificationSettings.emailPassword" type="password" placeholder="邮箱密码或授权码"
                            show-password />
                    </el-form-item>
                </el-form>
            </el-tab-pane>
        </el-tabs>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('basic')

// 基本设置
const basicSettings = ref({
    systemName: 'Encan考勤系统',
    companyName: '某某科技有限公司',
    workStartTime: new Date(2024, 0, 1, 9, 0),
    workEndTime: new Date(2024, 0, 1, 18, 0),
    workDays: ['1', '2', '3', '4', '5']
})

// 考勤规则
const attendanceRules = ref({
    lateThreshold: 15,
    earlyLeaveThreshold: 15,
    overtimeThreshold: 30,
    specialDates: ['2024-01-01', '2024-02-10']
})

// 通知设置
const notificationSettings = ref({
    emailEnabled: false,
    events: ['late', 'absent'],
    smtpServer: '',
    smtpPort: 465,
    senderEmail: '',
    emailPassword: ''
})

// 添加特殊日期
const handleAddSpecialDate = () => {
    // TODO: 实现添加特殊日期的逻辑
    console.log('添加特殊日期')
}

// 移除特殊日期
const handleRemoveDate = (date: string) => {
    const index = attendanceRules.value.specialDates.indexOf(date)
    if (index !== -1) {
        attendanceRules.value.specialDates.splice(index, 1)
    }
}

// 保存设置
const handleSave = () => {
    // TODO: 实现保存设置的逻辑
    ElMessage.success('设置保存成功')
}
</script>

<style scoped>
.settings-container {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.page-header h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
    color: #1a1a1a;
}

.settings-tabs {
    background: #ffffff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.separator {
    margin: 0 12px;
    color: #64748b;
}

.rule-hint {
    margin-left: 12px;
    font-size: 13px;
    color: #64748b;
}

.special-dates {
    margin-top: 12px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
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

:deep(.el-form-item) {
    margin-bottom: 24px;
}

:deep(.el-checkbox-group) {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
}
</style>