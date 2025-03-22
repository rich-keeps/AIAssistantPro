<script setup lang="ts">
import { ElConfigProvider } from 'element-plus'
import { Calendar, Setting, Cpu, Document } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'
import { computed, ref, onMounted, watch } from 'vue'
import axios from 'axios'

const route = useRoute()
const activeMenu = computed(() => route.path)

// 系统名称
const systemName = ref('AI智能化管理系统')

// 系统主题色
const themeColor = ref('#4CAF50')

// Element Plus 全局配置
const buttonConfig = {
    autoInsertSpace: true
}

// 获取系统设置
const fetchSystemSettings = async () => {
    try {
        const response = await axios.get('/api/settings/system')
        if (response.data.success && response.data.data) {
            const settings = response.data.data
            if (settings.system_name) {
                systemName.value = settings.system_name
            }
            if (settings.theme_color) {
                themeColor.value = settings.theme_color
                applyThemeColor(settings.theme_color)
            }
        }
    } catch (error) {
        console.error('获取系统设置失败:', error)
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

// 监听系统名称变化，更新浏览器标题
watch(systemName, (newName) => {
    document.title = newName
}, { immediate: true })

// 页面加载时获取系统设置
onMounted(() => {
    fetchSystemSettings()
})
</script>

<template>
    <el-config-provider :button-config="buttonConfig">
        <div class="app-wrapper">
            <!-- 侧边栏 -->
            <div class="sidebar">
                <div class="logo">
                    <div class="logo-icon">
                        <el-icon>
                            <Cpu />
                        </el-icon>
                    </div>
                    <span>{{ systemName }}</span>
                </div>

                <el-menu :default-active="activeMenu" router>
                    <el-menu-item index="/excel-processor">
                        <el-icon>
                            <Calendar />
                        </el-icon>
                        <span>考勤管理</span>
                    </el-menu-item>
                    <el-menu-item index="/report">
                        <el-icon>
                            <Document />
                        </el-icon>
                        <span>报表生成</span>
                    </el-menu-item>
                    <el-menu-item index="/settings">
                        <el-icon>
                            <Setting />
                        </el-icon>
                        <span>系统设置</span>
                    </el-menu-item>
                </el-menu>

                <!-- 工作区选择器 -->
                <div class="workspace-selector">
                    <div class="workspace-info">
                        <el-avatar class="workspace-avatar" :size="32">{{ '研' }}</el-avatar>
                        <div class="workspace-text">
                            <div class="workspace-name">研发部</div>
                            <div class="workspace-role">管理员</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 主内容区 -->
            <div class="main-container">
                <!-- 顶部导航 -->
                <div class="navbar">
                    <div class="right-menu">
                        <div class="user-profile">
                            <el-avatar class="user-avatar" :size="40">{{ '管' }}</el-avatar>
                            <div class="user-info">
                                <div class="user-name">管理员</div>
                                <div class="user-title">系统管理员</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 内容区 -->
                <div class="app-main">
                    <router-view></router-view>
                </div>
            </div>
        </div>
    </el-config-provider>
</template>

<style>
:root {
    --primary-color: #4CAF50;
    --sidebar-width: 280px;
    --header-height: 70px;
    --bg-color: #e8f5e9;

    /* Element Plus 主题色变量 */
    --el-color-primary: var(--primary-color);
    --el-color-primary-light-3: #81c784;
    --el-color-primary-light-5: #a5d6a7;
    --el-color-primary-light-7: #c8e6c9;
    --el-color-primary-light-8: #dcedc8;
    --el-color-primary-light-9: #f1f8e9;
    --el-color-primary-dark-2: #388e3c;

    /* 添加焦点边框颜色 */
    --el-color-primary-light-2: #66bb6a;
    --el-border-color-hover: #81c784;
    --el-border-color-focus: #66bb6a;
}

/* 添加全局样式覆盖Element Plus的焦点样式 */
.el-button:focus,
.el-button:active,
.el-input:focus,
.el-input:active,
.el-select:focus,
.el-select:active,
.el-checkbox:focus,
.el-checkbox:active {
    border-color: var(--el-color-primary) !important;
    outline-color: var(--el-color-primary) !important;
    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2) !important;
}

/* 覆盖Element Plus的focus-visible样式 */
.el-button:focus-visible,
.el-input:focus-visible,
.el-select:focus-visible,
.el-checkbox:focus-visible {
    outline: 2px solid var(--el-color-primary) !important;
    outline-offset: 1px !important;
    border-color: var(--el-color-primary) !important;
}

body {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    background-color: var(--bg-color);
}

.app-wrapper {
    display: flex;
    width: 100%;
    min-height: 100vh;
    padding: 15px;
    box-sizing: border-box;
    background-color: var(--bg-color);
    gap: 15px;
}

/* 侧边栏样式 */
.sidebar {
    width: var(--sidebar-width);
    height: calc(100vh - 30px);
    background: #ffffff;
    display: flex;
    flex-direction: column;
    padding: 24px;
    box-sizing: border-box;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    flex-shrink: 0;
}

.logo {
    height: 48px;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 12px;
    margin-bottom: 32px;
}

.logo-icon {
    width: 32px;
    height: 32px;
    background: var(--primary-color);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-size: 20px;
}

.logo span {
    font-size: 18px;
    font-weight: 600;
    color: #1a1a1a;
}

.el-menu {
    border: none !important;
    margin: 0 -24px;
    padding: 0 12px;
}

.el-menu-item {
    height: 44px !important;
    border-radius: 8px;
    margin: 4px 12px;
    color: #64748b !important;
}

.el-menu-item:hover {
    background: #f1f5f9 !important;
}

.el-menu-item.is-active {
    background: #e8f5e9 !important;
    color: var(--primary-color) !important;
}

.el-menu-item .el-icon {
    color: inherit;
}

/* 工作区选择器 */
.workspace-selector {
    margin-top: auto;
    padding: 16px;
    background: #f8fafc;
    border-radius: 12px;
    cursor: pointer;
}

.workspace-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.workspace-avatar {
    background: var(--primary-color);
}

.workspace-text {
    flex: 1;
}

.workspace-name {
    font-size: 14px;
    font-weight: 500;
    color: #1a1a1a;
}

.workspace-role {
    font-size: 12px;
    color: #64748b;
}

/* 主容器样式 */
.main-container {
    flex: 1;
    height: calc(100vh - 30px);
    background-color: #ffffff;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

/* 顶部导航样式 */
.navbar {
    height: var(--header-height);
    background: #ffffff;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 0 32px;
    border-bottom: 1px solid #e5e7eb;
}

.right-menu {
    display: flex;
    align-items: center;
}

.user-profile {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
}

.user-info {
    text-align: center;
}

.user-name {
    font-size: 14px;
    font-weight: 500;
    color: #1a1a1a;
}

.user-title {
    font-size: 12px;
    color: #64748b;
}

/* 主内容区样式 */
.app-main {
    padding: 32px;
    height: calc(100% - var(--header-height));
    overflow-y: auto;
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
    :root {
        --sidebar-width: 80px;
    }

    .logo span,
    .el-menu-item span,
    .workspace-text {
        display: none;
    }

    .workspace-selector {
        padding: 12px;
        display: flex;
        justify-content: center;
    }

    .workspace-info {
        justify-content: center;
    }
}
</style>