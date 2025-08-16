<template>
  <div class="not-found-view">
    <h1>404 - 页面未找到</h1>
    <p>您访问的页面不存在或已被移除</p>
    <button @click="goHome">返回首页</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goHome = () => {
  router.push({ name: 'home' });
};
</script>

<style scoped>
.not-found-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 70vh;
  text-align: center;
}

.not-found-view h1 {
  font-size: 2.5rem;
  margin-bottom: 20px;
}

.not-found-view p {
  font-size: 1.2rem;
  margin-bottom: 30px;
  color: #666;
}

.not-found-view button {
  padding: 10px 30px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

.not-found-view button:hover {
  background: #2980b9;
}
</style>