<template>
  <div class="not-found-view">
    <el-result icon="warning" title="页面不存在" sub-title="当前地址没有对应页面，请从左侧导航返回已预留模块。">
      <template #extra>
        <el-button type="primary" @click="router.push('/dashboard')">
          返回工作台
        </el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<style scoped>
.not-found-view {
  display: grid;
  place-items: center;
  min-height: 100vh;
  padding: 24px;
  background: var(--dmms-color-page);
}
</style>
