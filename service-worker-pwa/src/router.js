import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    component: () => import('@/pages/Dashboard.vue'),
    name: 'Dashboard',
    meta: { title: '工作台' }
  },
  {
    path: '/orders',
    component: () => import('@/pages/OrderHall.vue'),
    name: 'OrderHall',
    meta: { title: '抢单大厅' }
  },
  {
    path: '/orders/:id',
    component: () => import('@/pages/OrderDetail.vue'),
    name: 'OrderDetail',
    meta: { title: '订单详情' }
  },
  {
    path: '/calendar',
    component: () => import('@/pages/Calendar.vue'),
    name: 'Calendar',
    meta: { title: '日程日历' }
  },
  {
    path: '/wallet',
    component: () => import('@/pages/Wallet.vue'),
    name: 'Wallet',
    meta: { title: '我的钱包' }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守卫 - 检查离线状态
router.beforeEach((to, from, next) => {
  document.title = to.meta?.title || '';
  
  if (!navigator.onLine) {
    // 离线时允许访问部分页面
    if (['Dashboard', 'Wallet'].includes(to.name)) {
      next();
    } else {
      console.warn('离线模式下，部分功能不可用');
      // 仍然允许进入，但某些功能会禁用
      next();
    }
  } else {
    next();
  }
});

export default router;
