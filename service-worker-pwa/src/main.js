import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './style.css';

const app = createApp(App);
app.use(router);
app.mount('#app');

// 监听 PWA 安装/更新事件
window.addEventListener('activate', (event) => {
  console.log('PWA 激活:', event.reason);
  
  // 清理旧缓存
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== 'api-cache') {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
