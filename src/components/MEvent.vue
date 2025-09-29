<template>
  <div v-if="currentEvent" class="current-event">
    <h2 class="current-title">{{ currentEvent.title }}</h2>
    <div class="current-date">{{ currentEvent.date_tag }}</div>
    <div class="current-description">
      <div v-html="renderedDescription" class="markdown-content"></div>
      <div class="current-description-sentinel"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { marked } from 'marked'
import '@/assets/markdown-styles.css';

const props = defineProps({
  event: {
    type: Object,
    default: () => ({})
  },
  sentinelHeight: {
    type: String,
    default: "100vw"
  }
})

const currentEvent = computed(() => props.event)

const renderedDescription = computed(() => {
  if (currentEvent.value.description) {
    return marked.parse(currentEvent.value.description)
  }
  return ''
})

// #region 初始化
onMounted(() => {
  nextTick(() => {
    document.querySelector('.current-description-sentinel').style.height = props.sentinelHeight
  })
})
// #endregion

</script>

<style scoped>
/* #region 当前活动展示 */
.current-event {
  display: flex;
  flex-direction: column;
  max-height: 100%;
  overflow: scroll;

  background: rgba(255, 255, 255, 0.08);
  /* backdrop-filter: blur(10px); */
  background-color: #fff7f7c0;
  border-radius: 15px;
  padding: 20px 5px;
  margin: 15px 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;

  z-index: 5;
}

.current-date {
  font-size: 13px;
  color: #a0a0c0;
  text-align: right;
  margin-bottom: 10px;
  margin-right: 20px;
}

.current-title {
  font-size: 22px;
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: 0;
  text-align: center;
}

.current-description {
  font-size: 13px;
  overflow: auto;
}

.current-description-sentinel {
  height: 100vw;
}

/* #endregion */

</style>