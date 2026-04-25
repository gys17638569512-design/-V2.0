import 'vue-router'
import type { Component } from 'vue'

declare module 'vue-router' {
  interface RouteMeta {
    title: string
    description?: string
    featureModule?: string
    menuGroup?: string
    menuIcon?: Component
    hiddenInMenu?: boolean
    activeMenu?: string
  }
}
