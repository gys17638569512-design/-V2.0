import type { RouteMeta, RouteRecordRaw } from 'vue-router'
import {
  DataBoard,
  List,
  OfficeBuilding,
  UserFilled,
} from '@element-plus/icons-vue'

const createPlaceholderProps = (
  title: string,
  description: string,
  featureModule: string,
) => ({
  title,
  description,
  featureModule,
})

export interface AppRouteRecord {
  path: string
  name?: string
  component?: RouteRecordRaw['component']
  redirect?: RouteRecordRaw['redirect']
  props?: RouteRecordRaw['props']
  meta?: RouteMeta
  children?: AppRouteRecord[]
}

export const appRoutes: AppRouteRecord[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginPlaceholder.vue'),
    meta: {
      title: '登录入口',
      description: 'F02 将在这里接入登录页、Token 管理与路由守卫。',
      featureModule: 'F02',
      hiddenInMenu: true,
    },
  },
  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          title: '工作台',
          description: 'F01 基础框架首页已就位，当前仅承载导航入口与后续模块挂载位。',
          featureModule: 'F01',
          menuGroup: '工作台',
          menuIcon: DataBoard,
        },
      },
      {
        path: 'work-orders',
        name: 'WorkOrderList',
        component: () => import('@/components/AppPagePlaceholder.vue'),
        props: createPlaceholderProps(
          '工单中心',
          '这里预留 F04 工单列表与筛选入口，后续还会衔接 F05 派单抽屉和 F06 工单详情。',
          'F04-F06',
        ),
        meta: {
          title: '工单中心',
          description: '列表、筛选、状态流转入口都将在此挂载。',
          featureModule: 'F04-F06',
          menuGroup: '核心流程预留',
          menuIcon: List,
        },
      },
      {
        path: 'work-orders/:id',
        name: 'WorkOrderDetail',
        component: () => import('@/components/AppPagePlaceholder.vue'),
        props: createPlaceholderProps(
          '工单详情',
          '详情页路由已预留，后续将承接工单流程、执行记录与报告关联。',
          'F06',
        ),
        meta: {
          title: '工单详情',
          description: '详情页仅保留入口位置，不实现真实业务逻辑。',
          featureModule: 'F06',
          hiddenInMenu: true,
          activeMenu: '/work-orders',
        },
      },
      {
        path: 'customers',
        name: 'CustomerList',
        component: () => import('@/components/AppPagePlaceholder.vue'),
        props: createPlaceholderProps(
          '客户管理',
          '客户列表页入口已建立，后续将在这里接入客户筛选、分页与基础操作。',
          'F07',
        ),
        meta: {
          title: '客户管理',
          description: '客户列表与筛选将在这里补齐。',
          featureModule: 'F07',
          menuGroup: '核心流程预留',
          menuIcon: UserFilled,
        },
      },
      {
        path: 'customers/:id',
        name: 'CustomerDetail',
        component: () => import('@/components/AppPagePlaceholder.vue'),
        props: createPlaceholderProps(
          '客户详情',
          '客户详情页已预留，后续将作为设备、工单与联系人信息的聚合入口。',
          'F08',
        ),
        meta: {
          title: '客户详情',
          description: '详情页仅预留路由和承载位。',
          featureModule: 'F08',
          hiddenInMenu: true,
          activeMenu: '/customers',
        },
      },
      {
        path: 'equipments',
        name: 'EquipmentList',
        component: () => import('@/components/AppPagePlaceholder.vue'),
        props: createPlaceholderProps(
          '设备管理',
          '设备列表页路由已准备好，后续将在这里接入设备台账、筛选和状态信息。',
          'F09',
        ),
        meta: {
          title: '设备管理',
          description: '设备列表页后续将在此实现。',
          featureModule: 'F09',
          menuGroup: '核心流程预留',
          menuIcon: OfficeBuilding,
        },
      },
      {
        path: 'equipments/:id',
        name: 'EquipmentDetail',
        component: () => import('@/components/AppPagePlaceholder.vue'),
        props: createPlaceholderProps(
          '设备详情',
          '设备详情页已预留，后续将承接证书、维保记录与报告等信息。',
          'F10',
        ),
        meta: {
          title: '设备详情',
          description: '详情页仅预留路由和基础说明。',
          featureModule: 'F10',
          hiddenInMenu: true,
          activeMenu: '/equipments',
        },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: {
      title: '页面不存在',
      description: '当前访问的地址没有对应页面。',
      featureModule: 'F01',
      hiddenInMenu: true,
    },
  },
]

export const routerRoutes = appRoutes as RouteRecordRaw[]
