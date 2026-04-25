import { defineStore } from 'pinia'

export const useAppShellStore = defineStore('app-shell', {
  state: () => ({
    sidebarCollapsed: false,
  }),
  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
  },
})
