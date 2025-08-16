<template>
  <NavMobile v-if="isMobile" />
  <NavDesktop v-if="!isMobile" />
  <div class="page-container">
    <router-view v-if="isAllReady" class="content" />
  </div>
  <Footer></Footer>

</template>

<script setup>
import NavMobile from '@/components/NavMobile.vue'
import NavDesktop from '@/components/NavDesktop.vue'
import DataModel from '@/models/DataModel.js'
import Footer from '@/components/Footer.vue';
import StyleManager from '@/models/styleManager.js';

import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const REPO_URL = 'https://github.com/bpuffer/tsukimiya.site'
const isMobile = ref(false);
const route = useRoute();
const router = useRouter();
const isAllReady = ref(false)

const checkDeviceType = () => {
  const userChoice = localStorage.getItem('deviceType');
  if (userChoice) return userChoice === 'mobile';

  const ua = navigator.userAgent.toLowerCase();
  return /mobile|android|iphone|ipad|ipod/i.test(ua);
};

onMounted(async () => {
  console.log(`欢迎来到月宫の小站！翻阅源码请前往${REPO_URL}`)  // vite.config.js/build.terserOptions.compress.drop_console: false
  isMobile.value = checkDeviceType();
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
  background-image: url('@/assets/img/mbg.jpg');
  background-repeat: no-repeat;
  background-position: center center;
  background-size: cover;
  background-attachment: fixed;

  max-width: 100%;
  height: 100%;
}
/* body::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.5);
  z-index: -1;
} */

@media (min-width: 768px) {
  body {
    background-image: url('@/assets/img/mbg.jpg');
  }
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