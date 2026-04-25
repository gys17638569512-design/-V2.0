import type { Component } from 'vue'
import { appRoutes, type AppRouteRecord } from '@/router/routes'

export interface NavigationItem {
  title: string
  path: string
  icon: Component
  moduleCode: string
  description: string
}

export interface NavigationSection {
  title: string
  items: NavigationItem[]
}

const resolveRoutePath = (parentPath: string, routePath: string) => {
  if (routePath.startsWith('/')) {
    return routePath
  }

  const normalizedParent = parentPath === '/' ? '' : parentPath.replace(/\/$/, '')
  return `${normalizedParent}/${routePath}`.replace(/\/{2,}/g, '/')
}

const collectNavigationItems = (
  routes: AppRouteRecord[],
  parentPath = '',
): Array<NavigationItem & { sectionTitle: string }> =>
  routes.flatMap((route) => {
    const path = resolveRoutePath(parentPath, route.path)
    const meta = route.meta
    const sectionTitle = meta?.menuGroup
    const icon = meta?.menuIcon
    const item = meta && sectionTitle && icon && !meta.hiddenInMenu
      ? [{
        sectionTitle,
        title: meta.title,
        path,
        icon,
        moduleCode: meta.featureModule ?? '',
        description: meta.description ?? '',
      }]
      : []

    const childItems = route.children
      ? collectNavigationItems(route.children, path)
      : []

    return [...item, ...childItems]
  })

const navigationItems = collectNavigationItems(appRoutes)

export const navigationSections: NavigationSection[] = navigationItems.reduce<NavigationSection[]>(
  (sections, item) => {
    const existingSection = sections.find((section) => section.title === item.sectionTitle)

    const navigationItem: NavigationItem = {
      title: item.title,
      path: item.path,
      icon: item.icon,
      moduleCode: item.moduleCode,
      description: item.description,
    }

    if (existingSection) {
      existingSection.items.push(navigationItem)
      return sections
    }

    sections.push({
      title: item.sectionTitle,
      items: [navigationItem],
    })
    return sections
  },
  [],
)
