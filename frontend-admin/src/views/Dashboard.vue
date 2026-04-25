<template>
  <section class="dashboard-page">
    <el-card shadow="never" class="dashboard-page__hero">
      <div class="dashboard-page__hero-content">
        <div>
          <p class="dashboard-page__eyebrow">{{ APP_STAGE }}</p>
          <h2>{{ APP_NAME }}</h2>
          <p class="dashboard-page__summary">
            当前工作台仍属于 F01 基础框架承载页，已完成后台壳、路由骨架和核心模块入口预留；后续 F02-F10 可在不改信息架构的前提下逐步接入。
          </p>
        </div>
        <div class="dashboard-page__hero-tags">
          <el-tag>Vue 3 + TypeScript</el-tag>
          <el-tag type="success">Element Plus</el-tag>
          <el-tag type="warning">Pinia</el-tag>
        </div>
      </div>
    </el-card>

    <section class="dashboard-page__grid">
      <el-card
        v-for="section in navigationSections"
        :key="section.title"
        shadow="never"
        class="dashboard-page__card"
      >
        <template #header>
          <div class="dashboard-page__card-header">
            <span>{{ section.title }}</span>
            <el-tag effect="plain" size="small">{{ section.items.length }} 项</el-tag>
          </div>
        </template>

        <div class="dashboard-page__list">
          <button
            v-for="item in section.items"
            :key="item.path"
            class="dashboard-page__list-item"
            type="button"
            @click="router.push(item.path)"
          >
            <span class="dashboard-page__list-icon">
              <el-icon><component :is="item.icon" /></el-icon>
            </span>
            <span class="dashboard-page__list-text">
              <strong>{{ item.title }}</strong>
              <small>{{ item.description }}</small>
            </span>
            <el-tag effect="plain" size="small">{{ item.moduleCode }}</el-tag>
          </button>
        </div>
      </el-card>
    </section>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { APP_NAME, APP_STAGE } from '@/constants/app'
import { navigationSections } from '@/constants/navigation'

const router = useRouter()
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dashboard-page__hero {
  overflow: hidden;
  border-radius: 24px;
  background:
    radial-gradient(circle at top right, rgba(79, 140, 255, 0.16), transparent 28%),
    linear-gradient(145deg, #ffffff 0%, #f5f8ff 100%);
}

.dashboard-page__hero-content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.dashboard-page__eyebrow {
  margin-bottom: 8px;
  color: var(--dmms-color-text-secondary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.dashboard-page__hero h2 {
  margin-bottom: 12px;
  color: var(--dmms-color-text-primary);
  font-size: clamp(28px, 4vw, 36px);
}

.dashboard-page__summary {
  max-width: 720px;
  color: var(--dmms-color-text-secondary);
  line-height: 1.8;
}

.dashboard-page__hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.dashboard-page__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.dashboard-page__card {
  border-radius: 20px;
}

.dashboard-page__card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--dmms-color-text-primary);
  font-weight: 600;
}

.dashboard-page__list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dashboard-page__list-item {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
  padding: 14px;
  border: 1px solid var(--dmms-color-border);
  border-radius: 16px;
  background: var(--dmms-color-surface-muted);
  cursor: pointer;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    background 0.2s ease;
}

.dashboard-page__list-item:hover {
  border-color: rgba(35, 87, 215, 0.28);
  background: #fff;
  transform: translateY(-2px);
}

.dashboard-page__list-icon {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: rgba(35, 87, 215, 0.08);
  color: #2357d7;
}

.dashboard-page__list-text {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 4px;
  text-align: left;
}

.dashboard-page__list-text strong {
  color: var(--dmms-color-text-primary);
  font-size: 15px;
}

.dashboard-page__list-text small {
  color: var(--dmms-color-text-secondary);
  font-size: 13px;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .dashboard-page__hero-content {
    flex-direction: column;
  }
}
</style>
