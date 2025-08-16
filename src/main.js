import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

if (import.meta.env.DEV) {
  const loadTestData = async (datapath) => {
    datapath = datapath || '/test-data.json'
    try {
      localStorage.clear();
      localStorage.setItem('rawdata', await (await fetch(`/${datapath}`)).text());
      console.debug("测试数据已加载");
    } catch (error) {
      console.warn('加载测试数据失败:', error);
    }
  };

  // 加载测试数据集
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('ltd')) {
    loadTestData(urlParams.get('ltd') || null);
  }
}

createApp(App).use(router).mount('#app')