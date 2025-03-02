<script setup lang="ts">
import { ElConfigProvider } from 'element-plus'
</script>

<template>
  <el-config-provider>
    <el-container>
      <el-header>
        <h1>Excel数据处理工具</h1>
      </el-header>
      <el-main>
        <router-view></router-view>
      </el-main>
      <el-footer>
        <p>&copy; 2024 Excel数据处理工具</p>
      </el-footer>
    </el-container>
  </el-config-provider>
</template>

<style>
.el-header {
  background-color: #409EFF;
  color: white;
  text-align: center;
  line-height: 60px;
  padding: 0;
}

.el-footer {
  background-color: #f5f7fa;
  color: #606266;
  text-align: center;
  line-height: 60px;
  padding: 0;
}

.el-main {
  padding: 20px;
  min-height: calc(100vh - 120px);
}
</style>
