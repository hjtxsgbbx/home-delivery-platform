<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card daily-orders">
        <div class="stat-label">今日订单数</div>
        <div class="stat-value">{{ stats.dailyOrders }}</div>
        <div class="stat-trend">↑ {{ stats.trend }}%</div>
      </div>
      
      <div class="stat-card weekly-income">
        <div class="stat-label">本周收入</div>
        <div class="stat-value">{{ formatMoney(stats.weeklyIncome) }}</div>
        <div class="stat-trend">↑ {{ stats.trend }}%</div>
      </div>
      
      <div class="stat-card next-order">
        <div class="stat-label">下一单</div>
        <div class="stat-value" v-if="nextOrder">{{ nextOrder.time }}</div>
        <div class="stat-trend">{{ nextOrder?.orderType || '-' }}</div>
      </div>
    </div>

    <!-- 今日订单列表 -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">今日订单</h3>
        <span class="badge badge-success">{{ stats.completedOrders }} 已完成</span>
      </div>
      
      <div v-if="loading" class="loading"><div class="spinner"></div></div>
      
      <div v-else class="orders-list">
        <div 
          v-for="order in todayOrders.slice(0, 5)" 
          :key="order.id" 
          class="list-item order-card"
          @click="goToOrder(order)"
        >
          <div class="avatar">{{ getOrderIcon(order.type) }}</div>
          <div class="list-content">
            <div class="list-title">{{ order.title || '订单' + (order.id || '') }}</div>
            <div class="list-subtitle">{{ formatTime(order.time) }}</div>
            <div class="order-status" :class="'status-' + getStatusClass(order.status)">
              {{ getOrderStatusText(order.status) }}
            </div>
          </div>
          <div v-if="order.price" class="price">¥{{ order.price }}</div>
        </div>

        <div v-if="todayOrders.length === 0" class="empty-state">
          <p>今日暂无订单</p>
        </div>
      </div>
    </div>

    <!-- 本周收入详情 -->
    <div class="card weekly-detail">
      <h3 class="card-title">本周收入明细</h3>
      
      <div v-if="weeklyData && !loading" class="income-breakdown">
        <div 
          v-for="(item, day) in weeklyData" 
          :key="day" 
          class="income-row"
        >
          <span class="day-name">{{ formatDay(day) }}</span>
          <span class="day-orders">{{ item.orders }}单</span>
          <span class="day-income">¥{{ item.total }}</span>
        </div>
      </div>

      <div v-else-if="loading" class="loading"><div class="spinner"></div></div>
      
      <div v-else class="empty-state">数据加载中...</div>
    </div>

    <!-- 快捷功能 -->
    <div class="quick-actions card">
      <h3 class="card-title">快捷入口</h3>
      <div class="grid">
        <router-link 
          v-for="{ icon, label, path } in quickActions" 
          :key="path"
          :to="path"
          class="grid-item"
        >
          <span class="grid-icon">{{ icon }}</span>
          <span class="grid-label">{{ label }}</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fetchStatsData, fetchTodayOrders, getOfflineData } from '@/services/api.js';
import { showToast } from '@/utils/toast.js';

const route = useRoute();
const router = useRouter();

// 状态
const loading = ref(true);
const stats = ref({
  dailyOrders: 0,
  completedOrders: 0,
  weeklyIncome: 0,
  trend: '12'
});

const todayOrders = ref([]);
const nextOrder = ref(null);
const weeklyData = ref({});

// PWA 离线数据缓存
const offlineCache = ref({});

onMounted(async () => {
  await loadData();
  
  // 检查离线状态并加载离线缓存
  if (!navigator.onLine) {
    showToast('当前处于离线模式，部分功能不可用', 'warning');
  }
});

async function loadData() {
  loading.value = true;
  
  try {
    const [statsData, ordersData] = await Promise.all([
      fetchStatsData(),
      fetchTodayOrders()
    ]);
    
    stats.value = statsData;
    todayOrders.value = ordersData;
    
    // 计算下一单
    if (ordersData.length > 0) {
      const nextPending = ordersData.find(o => ['pending', 'new'].includes(o.status));
      nextOrder.value = nextPending || null;
    }
    
    // 加载周收入数据（模拟）
    await loadWeeklyIncome();
  } catch (error) {
    console.error('加载数据失败:', error);
    showToast('数据加载失败，请检查网络', 'error');
    
    // 尝试使用离线缓存
    const cached = getOfflineData();
    if (cached) {
      offlineCache.value = cached;
      stats.value = cached.stats || {};
      todayOrders.value = cached.orders || [];
    }
  } finally {
    loading.value = false;
  }
}

async function loadWeeklyIncome() {
  // 模拟周收入数据
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
  weeklyData.value = {};
  
  for (let i = 0; i < days.length; i++) {
    const date = new Date();
    date.setDate(date.getDate() - (6 - i));
    
    // 使用 localStorage 存储离线数据
    const key = `weekly_income_${date.toDateString()}`;
    const cached = localStorage.getItem(key);
    
    if (cached) {
      weeklyData.value[days[i]] = JSON.parse(cached);
    } else {
      // 模拟数据
      weeklyData.value[days[i]] = {
        orders: Math.floor(Math.random() * 20),
        total: Math.floor(Math.random() * 500) + 100
      };
      
      // 缓存到 localStorage
      localStorage.setItem(key, JSON.stringify(weeklyData.value[days[i]]));
    }
  }
}

function goToOrder(order) {
  router.push(`/orders/${order.id}`);
}

function getOrderIcon(type) {
  const icons = {
    'delivery': '📦',
    'repair': '🔧',
    'cleaning': '✨',
    'default': '💼'
  };
  return icons[type] || icons.default;
}

function getOrderStatusText(status) {
  const texts = {
    pending: '待接单',
    new: '新订单',
    active: '服务中',
    completed: '已完成',
    cancelled: '已取消'
  };
  return texts[status] || status;
}

function getStatusClass(status) {
  const classes = {
    pending: 'warning',
    new: 'success',
    active: '',
    completed: 'success',
    cancelled: 'danger'
  };
  return classes[status];
}

function formatMoney(amount) {
  return parseFloat(amount).toFixed(2);
}

function formatTime(timeStr) {
  if (!timeStr) return '';
  const date = new Date(timeStr);
  return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
}

function formatDay(day) {
  if (day === '今天') return '今日';
  if (['周一', '周二', '周三', '周五'].includes(day)) {
    return day + '（工作日）';
  }
  return day + '（休息日）';
}

const quickActions = [
  { icon: '📍', label: '抢单大厅', path: '/orders' },
  { icon: '📅', label: '日程日历', path: '/calendar' },
  { icon: '💰', label: '我的钱包', path: '/wallet' }
];

</script>

<style scoped>
.dashboard {
  padding-bottom: 80px; /* 为底部导航留空间 */
}

.stats-grid {
  display: grid;
  gap: 12px;
  margin-bottom: 16px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stat-label {
  font-size: 13px;
  color: #999;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.stat-trend {
  font-size: 12px;
  color: #52c41a;
}

.orders-list .order-card {
  cursor: pointer;
  transition: all 0.2s;
}

.order-card:active {
  transform: scale(0.98);
}

.empty-state {
  text-align: center;
  padding: 40px 16px;
  color: #999;
}

.weekly-detail .income-breakdown {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.income-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.income-row:last-child {
  border-bottom: none;
}

.quick-actions .grid {
  grid-template-columns: repeat(3, 1fr);
}
</style>
