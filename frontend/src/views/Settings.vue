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
                    <el-form-item label="主题色">
                        <div class="theme-color-wrapper">
                            <!-- 颜色选择区域 -->
                            <div class="color-selection-area">
                                <div class="color-squares">
                                    <!-- 预设颜色方块 -->
                                    <div class="color-square" v-for="color in presetColors" :key="color"
                                        :class="{ active: basicSettings.themeColor === color }"
                                        :style="{ borderColor: basicSettings.themeColor === color ? color : 'transparent' }"
                                        @click="selectColor(color)">
                                        <div class="inner-square" :style="{ backgroundColor: color }"></div>
                                    </div>
                                </div>
                                <div class="color-hint">选择系统主题色，将影响整个系统的颜色风格</div>
                            </div>

                            <!-- 预览效果区域 -->
                            <div class="preview-container">
                                <div class="preview-header">预览效果</div>
                                <div class="preview-content">
                                    <div class="preview-description">以下是主题色应用后的效果预览，保存后将应用到整个系统</div>

                                    <div class="preview-demo">
                                        <div class="theme-title" :style="{ backgroundColor: basicSettings.themeColor }">
                                            主题色标题
                                        </div>

                                        <div class="preview-controls">
                                            <div class="control-row">
                                                <div class="control-label">按钮：</div>
                                                <div class="control-content">
                                                    <el-button type="primary" :style="{
                                                        '--el-button-bg-color': basicSettings.themeColor,
                                                        '--el-button-border-color': basicSettings.themeColor
                                                    }">主要按钮</el-button>
                                                    <el-button plain :style="{
                                                        borderColor: basicSettings.themeColor,
                                                        color: basicSettings.themeColor
                                                    }">补素按钮</el-button>
                                                </div>
                                            </div>

                                            <div class="control-row">
                                                <div class="control-label">标签：</div>
                                                <div class="control-content">
                                                    <el-tag :style="{
                                                        backgroundColor: lightenColor(basicSettings.themeColor, 90),
                                                        borderColor: lightenColor(basicSettings.themeColor, 80),
                                                        color: basicSettings.themeColor
                                                    }">标签</el-tag>
                                                    <el-tag type="info">普通标签</el-tag>
                                                </div>
                                            </div>

                                            <div class="control-row">
                                                <div class="control-label">开关：</div>
                                                <div class="control-content">
                                                    <el-switch v-model="previewSwitch"
                                                        :style="{ '--el-switch-on-color': basicSettings.themeColor }" />
                                                    <span class="status-text">开启</span>
                                                </div>
                                            </div>

                                            <div class="control-row">
                                                <div class="control-label">复选框：</div>
                                                <div class="control-content">
                                                    <el-checkbox v-model="previewCheckbox"
                                                        :style="{ '--el-checkbox-checked-bg-color': basicSettings.themeColor }">选项</el-checkbox>
                                                </div>
                                            </div>

                                            <div class="control-row">
                                                <div class="control-label">单选框：</div>
                                                <div class="control-content">
                                                    <el-radio v-model="previewRadio" :label="1"
                                                        :style="{ '--el-radio-checked-bg-color': basicSettings.themeColor }">选项1</el-radio>
                                                    <el-radio v-model="previewRadio" :label="2"
                                                        :style="{ '--el-radio-checked-bg-color': basicSettings.themeColor }">选项2</el-radio>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </el-form-item>
                </el-form>
            </el-tab-pane>

            <!-- 文件管理 -->
            <el-tab-pane label="文件管理" name="files">
                <el-form :model="fileSettings" label-width="160px">
                    <el-form-item label="最大文件数量">
                        <el-input-number v-model="fileSettings.maxFiles" :min="10" :max="1000" :step="10"
                            placeholder="最大文件数量" />
                        <span class="rule-hint">超过此数量将自动清理最旧的文件</span>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="danger" @click="handleCleanFiles">立即清理文件</el-button>
                    </el-form-item>
                </el-form>
            </el-tab-pane>
        </el-tabs>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const activeTab = ref('basic')

// 基本设置
const basicSettings = ref({
    systemName: 'Encan考勤系统',
    themeColor: '#4CAF50'
})

// 保存当前应用的主题色，用于比较是否有变化
const currentAppliedTheme = ref('#4CAF50')

// 文件设置
const fileSettings = ref({
    maxFiles: 100
})

// 预设颜色
const presetColors = ref([
    '#F5A623', // 橙色
    '#4CAF50', // 绿色
    '#2196F3', // 蓝色
    '#9C27B0', // 紫色
    '#F44336', // 红色
])

// 获取系统设置
const fetchSystemSettings = async () => {
    try {
        const response = await axios.get('/api/settings/system')
        if (response.data.success) {
            const settings = response.data.data
            if (settings.max_files) {
                fileSettings.value.maxFiles = settings.max_files
            }
            if (settings.system_name) {
                basicSettings.value.systemName = settings.system_name
            }
            if (settings.theme_color) {
                basicSettings.value.themeColor = settings.theme_color
                currentAppliedTheme.value = settings.theme_color
                // 应用主题色
                applyThemeColor(settings.theme_color)
            }
            ElMessage.success('系统设置加载成功')
        }
    } catch (error) {
        console.error('获取系统设置失败:', error)
        ElMessage.error('获取系统设置失败')
    }
}

// 应用主题色
const applyThemeColor = (color: string) => {
    // 设置CSS变量
    document.documentElement.style.setProperty('--primary-color', color)
    document.documentElement.style.setProperty('--el-color-primary', color)

    // 生成不同亮度的主题色变体
    const generateLighterColor = (color: string, percent: number) => {
        const r = parseInt(color.slice(1, 3), 16)
        const g = parseInt(color.slice(3, 5), 16)
        const b = parseInt(color.slice(5, 7), 16)

        const lightenValue = (value: number, percent: number) => {
            return Math.min(255, Math.floor(value + (255 - value) * percent / 100))
        }

        const rLighter = lightenValue(r, percent)
        const gLighter = lightenValue(g, percent)
        const bLighter = lightenValue(b, percent)

        return `#${rLighter.toString(16).padStart(2, '0')}${gLighter.toString(16).padStart(2, '0')}${bLighter.toString(16).padStart(2, '0')}`
    }

    const generateDarkerColor = (color: string, percent: number) => {
        const r = parseInt(color.slice(1, 3), 16)
        const g = parseInt(color.slice(3, 5), 16)
        const b = parseInt(color.slice(5, 7), 16)

        const darkenValue = (value: number, percent: number) => {
            return Math.max(0, Math.floor(value * (100 - percent) / 100))
        }

        const rDarker = darkenValue(r, percent)
        const gDarker = darkenValue(g, percent)
        const bDarker = darkenValue(b, percent)

        return `#${rDarker.toString(16).padStart(2, '0')}${gDarker.toString(16).padStart(2, '0')}${bDarker.toString(16).padStart(2, '0')}`
    }

    // 设置不同亮度的主题色变体
    document.documentElement.style.setProperty('--el-color-primary-light-3', generateLighterColor(color, 30))
    document.documentElement.style.setProperty('--el-color-primary-light-5', generateLighterColor(color, 50))
    document.documentElement.style.setProperty('--el-color-primary-light-7', generateLighterColor(color, 70))
    document.documentElement.style.setProperty('--el-color-primary-light-8', generateLighterColor(color, 80))
    document.documentElement.style.setProperty('--el-color-primary-light-9', generateLighterColor(color, 90))
    document.documentElement.style.setProperty('--el-color-primary-dark-2', generateDarkerColor(color, 20))
    document.documentElement.style.setProperty('--el-color-primary-light-2', generateLighterColor(color, 20))
    document.documentElement.style.setProperty('--el-border-color-hover', generateLighterColor(color, 30))
    document.documentElement.style.setProperty('--el-border-color-focus', generateLighterColor(color, 20))
}

// 立即清理文件
const handleCleanFiles = async () => {
    try {
        await ElMessageBox.confirm(
            '确定要立即清理文件吗？这将删除最旧的文件，直到文件数量低于设定的最大值。',
            '确认清理',
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }
        )

        // 调用清理文件API
        const response = await axios.post('/api/settings/clean-files')
        if (response.data.success) {
            ElMessage.success('文件清理成功')
        } else {
            ElMessage.error(response.data.message || '文件清理失败')
        }
    } catch (error) {
        if (error !== 'cancel') {
            console.error('文件清理失败:', error)
            ElMessage.error('文件清理失败')
        }
    }
}

// 保存所有设置
const handleSave = async () => {
    try {
        const response = await axios.put('/api/settings/system', {
            system_name: basicSettings.value.systemName,
            max_files: fileSettings.value.maxFiles,
            theme_color: basicSettings.value.themeColor
        })
        if (response.data.success) {
            // 保存成功后应用新的主题色
            if (currentAppliedTheme.value !== basicSettings.value.themeColor) {
                applyThemeColor(basicSettings.value.themeColor)
                currentAppliedTheme.value = basicSettings.value.themeColor
            }
            ElMessage.success('设置保存成功')
        }
    } catch (error) {
        console.error('保存设置失败:', error)
        ElMessage.error('保存设置失败')
    }
}

// 页面加载时获取系统设置
onMounted(() => {
    fetchSystemSettings()
})

// 预览相关状态
const previewSwitch = ref(true)
const previewCheckbox = ref(true)
const previewRadio = ref(1)

// 辅助函数：生成更亮的颜色
const lightenColor = (color: string, percent: number) => {
    const r = parseInt(color.slice(1, 3), 16)
    const g = parseInt(color.slice(3, 5), 16)
    const b = parseInt(color.slice(5, 7), 16)

    const lightenValue = (value: number, percent: number) => {
        return Math.min(255, Math.floor(value + (255 - value) * percent / 100))
    }

    const rLighter = lightenValue(r, percent)
    const gLighter = lightenValue(g, percent)
    const bLighter = lightenValue(b, percent)

    return `#${rLighter.toString(16).padStart(2, '0')}${gLighter.toString(16).padStart(2, '0')}${bLighter.toString(16).padStart(2, '0')}`
}

// 选择预设颜色
const selectColor = (color: string) => {
    basicSettings.value.themeColor = color
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

.theme-color-wrapper {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

/* 颜色选择区域 */
.color-selection-area {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.color-squares {
    display: flex;
    gap: 12px;
}

.color-square {
    width: 40px;
    height: 40px;
    border-radius: 4px;
    border: 2px solid transparent;
    padding: 2px;
    cursor: pointer;
    transition: all 0.2s;
}

.color-square:hover {
    transform: scale(1.05);
}

.color-square.active {
    border-width: 2px;
}

.inner-square {
    width: 100%;
    height: 100%;
    border-radius: 2px;
}

.color-hint {
    font-size: 13px;
    color: #606266;
    margin-top: 4px;
}

/* 预览效果区域 */
.preview-container {
    margin-top: 20px;
    border: 1px solid #ebeef5;
    border-radius: 8px;
    overflow: hidden;
    background-color: #f5f7fa;
}

.preview-header {
    padding: 15px 20px;
    font-size: 16px;
    font-weight: 500;
    color: #303133;
    border-bottom: 1px solid #ebeef5;
}

.preview-content {
    padding: 0 0 20px;
}

.preview-description {
    padding: 15px 20px;
    font-size: 13px;
    color: #606266;
}

.preview-demo {
    margin: 0 20px;
    border: 1px solid #ebeef5;
    border-radius: 6px;
    overflow: hidden;
    background-color: #fff;
}

.theme-title {
    padding: 12px 16px;
    color: #fff;
    font-weight: 500;
    font-size: 14px;
}

.preview-controls {
    padding: 20px;
}

.control-row {
    display: flex;
    margin-bottom: 20px;
    align-items: center;
}

.control-row:last-child {
    margin-bottom: 0;
}

.control-label {
    width: 80px;
    font-size: 14px;
    color: #606266;
    text-align: right;
    padding-right: 12px;
    line-height: 32px;
}

.control-content {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 12px;
}

.status-text {
    margin-left: 8px;
    font-size: 14px;
    color: #606266;
}

/* 确保组件颜色正确 */
:deep(.el-switch.is-checked .el-switch__core) {
    background-color: var(--el-switch-on-color, var(--el-color-primary)) !important;
    border-color: var(--el-switch-on-color, var(--el-color-primary)) !important;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
    background-color: var(--el-checkbox-checked-bg-color, var(--el-color-primary)) !important;
    border-color: var(--el-checkbox-checked-bg-color, var(--el-color-primary)) !important;
}

:deep(.el-radio__input.is-checked .el-radio__inner) {
    background-color: var(--el-radio-checked-bg-color, var(--el-color-primary)) !important;
    border-color: var(--el-radio-checked-bg-color, var(--el-color-primary)) !important;
}

/* 确保复选框和单选框的颜色正确 */
:deep(.el-checkbox__inner::after) {
    border-color: #fff !important;
}

:deep(.el-radio__inner::after) {
    background-color: #fff !important;
}

/* 确保开关的颜色正确 */
:deep(.el-switch__core .el-switch__action) {
    background-color: #fff !important;
}

/* 移除旧样式 */
.preview-box,
.preview-row,
.row-label,
.row-content,
.switch-wrapper,
.checkbox-wrapper,
.radio-wrapper,
.switch-text {
    /* 这些类将被新的样式替代 */
}
</style>