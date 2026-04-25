<template>
  <div class="app-shell">
    <aside :class="['app-shell__sidebar', { 'is-collapsed': sidebarCollapsed }]">
      <div class="app-shell__brand">
        <div class="app-shell__brand-mark">DMMS</div>
        <div v-if="!sidebarCollapsed" class="app-shell__brand-text">
          <strong>{{ APP_NAME }}</strong>
          <span>{{ APP_SUBTITLE }}</span>
        </div>
      </div>

      <div class="app-shell__menu">
        <section
          v-for="section in navigationSections"
          :key="section.title"
          class="app-shell__menu-section"
        >
          <p v-if="!sidebarCollapsed" class="app-shell__menu-title">
            {{ section.title }}
          </p>
          <el-menu
            :collapse="sidebarCollapsed"
            :collapse-transition="false"
            :default-active="activeMenuPath"
            router
            class="app-shell__menu-list"
          >
            <el-menu-item
              v-for="item in section.items"
              :key="item.path"
              :index="item.path"
            >
              <el-icon><component :is="item.icon" /></el-icon>
              <template #title>
                <span>{{ item.title }}</span>
              </template>
            </el-menu-item>
          </el-menu>
        </section>
      </div>
    </aside>

    <div class="app-shell__main">
      <header class="app-shell__header">
        <div class="app-shell__header-left">
          <el-button circle text @click="appShellStore.toggleSidebar()">
            <el-icon><Fold /></el-icon>
          </el-button>
          <div>
            <h1>{{ currentTitle }}</h1>
            <p>{{ currentDescription }}</p>
          </div>
        </div>
        <div class="app-shell__header-right">
          <el-tag effect="plain">{{ APP_STAGE }}</el-tag>
        </div>
      </header>

      <main class="app-shell__content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Fold } from '@element-plus/icons-vue'
import { storeToRefs } from 'pinia'
import { useRoute } from 'vue-router'
import { APP_NAME, APP_STAGE, APP_SUBTITLE } from '@/constants/app'
import { navigationSections } from '@/constants/navigation'
import { useAppShellStore } from '@/stores/app-shell'

const route = useRoute()
const appShellStore = useAppShellStore()
const { sidebarCollapsed } = storeToRefs(appShellStore)

const currentTitle = computed(() => route.meta.title)
const currentDescription = computed(
  () => route.meta.description ?? '基础后台框架已就位，后续模块可在此自然挂载。',
)
const activeMenuPath = computed(
  () => route.meta.activeMenu ?? route.path,
)
</script>

<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(28, 99, 214, 0.08), transparent 30%),
    linear-gradient(180deg, #f5f7fb 0%, #eef2f8 100%);
}

.app-shell__sidebar {
  display: flex;
  flex-direction: column;
  width: 248px;
  padding: 20px 16px;
  border-right: 1px solid var(--dmms-color-border);
  background: rgba(12, 22, 40, 0.94);
  color: #fff;
  transition: width 0.2s ease;
}

.app-shell__sidebar.is-collapsed {
  width: 80px;
}

.app-shell__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;
  padding: 0 6px;
}

.app-shell__brand-mark {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: linear-gradient(135deg, #4f8cff 0%, #2357d7 100%);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.app-shell__brand-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.app-shell__brand-text strong {
  font-size: 14px;
  line-height: 1.3;
}

.app-shell__brand-text span {
  color: rgba(255, 255, 255, 0.68);
  font-size: 12px;
}

.app-shell__menu {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 18px;
}

.app-shell__menu-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.app-shell__menu-title {
  padding: 0 12px;
  color: rgba(255, 255, 255, 0.45);
  font-size: 12px;
  letter-spacing: 0.06em;
}

.app-shell__menu-list {
  border-right: none;
  background: transparent;
}

.app-shell__menu-list :deep(.el-menu-item) {
  height: 44px;
  margin-bottom: 4px;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.74);
}

.app-shell__menu-list :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.08);
}

.app-shell__menu-list :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(79, 140, 255, 0.26), rgba(79, 140, 255, 0.12));
  color: #fff;
}

.app-shell__menu-list :deep(.el-menu) {
  background: transparent;
}

.app-shell__main {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  min-width: 0;
}

.app-shell__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 28px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(14px);
  background: rgba(255, 255, 255, 0.72);
}

.app-shell__header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
}

.app-shell__header-left h1 {
  color: var(--dmms-color-text-primary);
  font-size: 22px;
  font-weight: 600;
}

.app-shell__header-left p {
  margin-top: 4px;
  color: var(--dmms-color-text-secondary);
  font-size: 13px;
}

.app-shell__content {
  padding: 24px 28px 28px;
  overflow: auto;
}

@media (max-width: 960px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .app-shell__sidebar {
    width: 100%;
    padding-bottom: 12px;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  }

  .app-shell__sidebar.is-collapsed {
    width: 100%;
  }

  .app-shell__menu {
    gap: 12px;
  }

  .app-shell__header,
  .app-shell__content {
    padding-right: 18px;
    padding-left: 18px;
  }
}

@media (max-width: 640px) {
  .app-shell__header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
