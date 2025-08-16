<template>
  <div class="view-container">
    <h1>{{ pageTitle }}</h1>
    <div class="content-placeholder">
      <p>{{ pageTitle }}功能开发中...</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const pageTitle = computed(() => route.meta.title);
</script>

<style scoped>
.view-container {
  padding: 20px;
}

.content-placeholder {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
  border-radius: 10px;
  margin-top: 20px;
}
</style>