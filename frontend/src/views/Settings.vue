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
            const settings = response.data.data || {}

            // 设置文件数量
            if (settings.max_files) {
                fileSettings.value.maxFiles = settings.max_files
            }

            // 设置系统名称
            if (settings.system_name) {
                basicSettings.value.systemName = settings.system_name
            }

            // 设置主题色（如果返回了主题色数据）
            if (settings.theme_color) {
                basicSettings.value.themeColor = settings.theme_color
                currentAppliedTheme.value = settings.theme_color
            }

            // 无论接口是否返回主题色，都应用当前设置中的主题色
            applyThemeColor(basicSettings.value.themeColor)
        }
    } catch (error) {
        console.error('获取系统设置失败:', error)
        ElMessage.error('获取系统设置失败')

        // 发生错误时，仍应用当前设置的主题色
        applyThemeColor(basicSettings.value.themeColor)
    }
}

// 应用主题色
const applyThemeColor = (color: string) => {
    // 创建根级CSS变量，使用Element Plus的变量命名规范
    document.documentElement.style.setProperty('--el-color-primary', color);

    // 使用CSS 颜色函数替代手动计算颜色变体
    // 亮色变体
    document.documentElement.style.setProperty('--el-color-primary-light-3', `color-mix(in srgb, ${color} 70%, white)`);
    document.documentElement.style.setProperty('--el-color-primary-light-5', `color-mix(in srgb, ${color} 50%, white)`);
    document.documentElement.style.setProperty('--el-color-primary-light-7', `color-mix(in srgb, ${color} 30%, white)`);
    document.documentElement.style.setProperty('--el-color-primary-light-8', `color-mix(in srgb, ${color} 20%, white)`);
    document.documentElement.style.setProperty('--el-color-primary-light-9', `color-mix(in srgb, ${color} 10%, white)`);

    // 暗色变体
    document.documentElement.style.setProperty('--el-color-primary-dark-2', `color-mix(in srgb, ${color} 80%, black)`);

    // 边框相关颜色
    document.documentElement.style.setProperty('--el-border-color-hover', `color-mix(in srgb, ${color} 70%, white)`);
    document.documentElement.style.setProperty('--el-border-color-focus', `color-mix(in srgb, ${color} 80%, white)`);
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
</style>