<template>
  <div class="announcement-card" :style="{ '--hue': announcement.hue }" ref="el">
    <div class="announcement-header">
      <div class="announcement-title">{{ announcement.title }}</div>
      <div class="announcement-date">{{ announcement.date }}</div>
    </div>
    <div class="announcement-content">{{ announcement.content }}</div>
    <div class="announcement-footer">
      <div v-for="tag in announcement.tag.split(',')">
        <div v-if="tag != ''" class="announcement-tag">{{ tag }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue';

const props = defineProps(
  {
    announcement: {
      type: Object,
      default: () => ({
        title: '-',
        date: '-',
        content: '-',
        tag: '',
        hue: 0
      })
    },
    isInFadeIn: {
      type: Boolean,
      default: false
    },
    isStatic: {
      type: Boolean,
      default: false
    }
  }
)

const el = ref(null);
watch(() => props.isInFadeIn, (newVal) => {
  if (newVal) {
    nextTick(() => {
      el.value.style.opacity = '1';
      el.value.style.transform = 'translateY(0)';
    })
  }
})

onMounted(() => {
  if (props.isStatic) {
    el.value.style.transition = 'none';
    el.value.style.opacity = '1';
    el.value.style.transform = 'translateY(0)';
  }
})

</script>

<style scoped>

.announcement-card {
  background: rgba(255, 255, 255, 0.75);
  border-radius: 20px;
  padding: 20px;
  border: 3px solid hsl(var(--hue), 100%, 80%);
  position: relative;
  overflow: hidden;
  transform: translateY(20px);
  opacity: 0;
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.announcement-title {
  font-size: 18px;
  font-weight: bold;
  color: #5a67d8;
  flex: 1;
  padding-right: 10px;
}

.announcement-date {
  font-size: 14px;
  color: #ff7eb8;
  white-space: nowrap;
}

.announcement-content {
  color: #4a5568;
  line-height: 1.6;
  margin-bottom: 15px;
  font-size: 16px;
  white-space: pre-line;
}

.announcement-footer {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px;

}

.announcement-tag {
  background: hsl(var(--hue), 100%, 90%);
  color: hsl(var(--hue), 60%, 40%);
  padding: 5px 15px;
  border-radius: 15px;
  font-size: 14px;
  font-weight: bold;
}
</style>