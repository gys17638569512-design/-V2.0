<template>
  <div class="login-placeholder">
    <section class="login-placeholder__hero">
      <span>F02 预留</span>
      <h1>{{ APP_NAME }}</h1>
      <p>这里只保留登录模块的正式入口位，认证逻辑、Token 管理和权限守卫将在后续模块接入。</p>
    </section>

    <el-card shadow="never" class="login-placeholder__card">
      <div class="login-placeholder__card-header">
        <h2>登录页占位</h2>
        <el-tag effect="plain" type="info">未接认证</el-tag>
      </div>
      <p>F01 仅完成路由、页面位置和整体视觉基调，不包含任何真实登录能力。</p>
      <el-button type="primary" plain @click="router.push('/dashboard')">
        返回后台框架
      </el-button>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { APP_NAME } from '@/constants/app'

const router = useRouter()
</script>

<style scoped>
.login-placeholder {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 420px);
  align-items: center;
  min-height: 100vh;
  padding: 32px;
  gap: 24px;
  background:
    radial-gradient(circle at top right, rgba(60, 118, 255, 0.18), transparent 32%),
    linear-gradient(135deg, #0c1630 0%, #16325c 100%);
}

.login-placeholder__hero {
  color: #fff;
}

.login-placeholder__hero span {
  display: inline-flex;
  margin-bottom: 16px;
  padding: 6px 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
}

.login-placeholder__hero h1 {
  margin-bottom: 16px;
  font-size: clamp(32px, 4vw, 52px);
  line-height: 1.1;
}

.login-placeholder__hero p {
  max-width: 560px;
  color: rgba(255, 255, 255, 0.74);
  font-size: 16px;
  line-height: 1.8;
}

.login-placeholder__card {
  border-radius: 24px;
}

.login-placeholder__card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.login-placeholder__card-header h2 {
  color: var(--dmms-color-text-primary);
  font-size: 24px;
}

.login-placeholder__card p {
  margin-bottom: 20px;
  color: var(--dmms-color-text-secondary);
  line-height: 1.8;
}

@media (max-width: 900px) {
  .login-placeholder {
    grid-template-columns: 1fr;
  }
}
</style>
