<template>
  <section class="placeholder-page">
    <header class="placeholder-page__header">
      <div>
        <div class="placeholder-page__eyebrow">{{ featureModule }}</div>
        <h1>{{ title }}</h1>
      </div>
      <el-tag effect="plain" type="info">路由已预留</el-tag>
    </header>

    <el-card shadow="never" class="placeholder-page__card">
      <p>{{ description }}</p>

      <div class="placeholder-page__timeline">
        <div class="placeholder-page__timeline-item">
          <span>当前阶段</span>
          <strong>F01 仅保留信息结构与挂载点</strong>
        </div>
        <div class="placeholder-page__timeline-item">
          <span>后续接入</span>
          <strong>{{ featureModule }} 将在此补齐真实页面逻辑</strong>
        </div>
        <div class="placeholder-page__timeline-item">
          <span>本次不做</span>
          <strong>不接接口、不做真实业务交互</strong>
        </div>
      </div>
    </el-card>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description: string
  featureModule: string
}>()
</script>

<style scoped>
.placeholder-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.placeholder-page__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.placeholder-page__eyebrow {
  margin-bottom: 8px;
  color: var(--dmms-color-text-secondary);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
}

.placeholder-page__header h1 {
  color: var(--dmms-color-text-primary);
  font-size: 24px;
  font-weight: 600;
}

.placeholder-page__card {
  border-radius: 20px;
}

.placeholder-page__card p {
  color: var(--dmms-color-text-secondary);
  line-height: 1.7;
}

.placeholder-page__timeline {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 20px;
}

.placeholder-page__timeline-item {
  padding: 16px;
  border: 1px solid var(--dmms-color-border);
  border-radius: 16px;
  background: var(--dmms-color-surface-muted);
}

.placeholder-page__timeline-item span {
  display: block;
  margin-bottom: 8px;
  color: var(--dmms-color-text-secondary);
  font-size: 12px;
}

.placeholder-page__timeline-item strong {
  color: var(--dmms-color-text-primary);
  font-size: 14px;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .placeholder-page__header {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
