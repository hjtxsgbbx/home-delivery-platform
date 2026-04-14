<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';

// 检查并请求服务 worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    // VitePWA 会自动注册 service worker
    console.log('Service Worker 已自动配置');
  });
}
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 隐藏滚动条但保持功能 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}
</style>
