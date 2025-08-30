<template>
  <div class="placeholder-container">
    <h1>{{ pageTitle }}</h1>
    <p>本页面为电脑端页面预留，开发完成前请使用手机访问。</p>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
const route = useRoute();
const pageTitle = computed(() => route.meta.title);
</script>

<style scoped>
.placeholder-container {
  padding: 20px;
}
</style>