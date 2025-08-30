<template>
  <div class="global-container">
    <div class="global-view-container">
      <NavMobile v-if="isMobile" />
      <NavDesktop v-if="!isMobile" />
      <div class="page-container">
        <router-view v-if="isAllReady" class="content" />
      </div>
    </div>
  </div>
</template>

<script setup>
import NavMobile from '@/components/NavMobile.vue'
import NavDesktop from '@/components/NavDesktop.vue'
import DataModel from '@/models/DataModel.js'
import StyleManager from '@/models/styleManager.js';

import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const REPO_URL = 'https://github.com/bpuffer/tsukimiya.site'
const isMobile = ref(false);
const route = useRoute();
const router = useRouter();
const isAllReady = ref(false)

const IsMobile = () => {
  return true;  // 暂时不支持电脑。

  const userChoice = localStorage.getItem('deviceType');
  if (userChoice) return userChoice === 'mobile';

  const ua = navigator.userAgent.toLowerCase();
  return /mobile|android|iphone|ipad|ipod/i.test(ua);
};

onMounted(async () => {
  console.log(`欢迎来到月宫の小站！翻阅源码请前往${REPO_URL}`)  // vite.config.js/build.terserOptions.compress.drop_console: false
  isMobile.value = IsMobile();
  await router.isReady();
  if (isMobile.value && !route.fullPath.startsWith("/m")) {
    router.push({ name: 'm' });
  }
  DataModel.init(localStorage.getItem('rawdata'))
  StyleManager.changeBg('default-m3'); 
  isAllReady.value = true
});
</script>

<style>
body {
  background-image: linear-gradient(180deg, #ffffff, #e6e6e6);
  background-repeat: no-repeat;
  background-position: center center;
  background-size: cover;
  background-attachment: fixed;

  max-width: 100%;
  height: 100%;
}

.global-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 如果大于768px，限制宽度 */
.global-view-container {
  width: 100%;
  max-width: 425px;
}

.content {
  padding: 15px;
  min-height: calc(100vh - 64px);
  background-color: transparent;
}

.page-container {
  display: flex;
  flex-direction: column;
}

@media (max-width: 425px) {
  .content {
    margin-left: 0;
  }
}
</style>