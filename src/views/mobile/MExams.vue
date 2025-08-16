<template>
  <div class="view-container">

    <MExamAll v-if="subpage == 'all'"></MExamAll>
    <MExamArrange v-if="subpage == 'arrange'"></MExamArrange>
    <MExamGrades v-if="subpage == 'grades'" :showDetails="subpageGradesShowDetail"></MExamGrades>

    <div class="subpage-bar">
      <div class="subpage-btn" :class="{ active: subpage === 'all' }" @click="subpage = 'all'">
        <i class="fas fa-list"></i> 全部科目
      </div>
      <div class="subpage-btn" :class="{ active: subpage === 'arrange' }" @click="subpage = 'arrange'">
        <i class="fas fa-clock"></i> 考试安排
      </div>
      <div class="subpage-btn" :class="{ active: subpage === 'grades' }" @click="subpageGrades">
        <span v-if="!subpageGradesShowDetail || subpage !== 'grades'">
          <i class="fa-solid fa-graduation-cap"></i>
          <span v-if="subpage !== 'grades'">考试成绩</span>
          <u v-else>考试成绩</u>
        </span>
        <span v-if="subpageGradesShowDetail && subpage === 'grades'">
          <i class="fa-solid fa-circle-info"></i>
          <span v-if="subpage !== 'grades'">成绩筛选</span>
          <u v-else>成绩筛选</u>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import DataModel from '@/models/DataModel';

import MExamAll from './MExamAll.vue'
import MExamArrange from './MExamArrange.vue'
import MExamGrades from './MExamGrades.vue'

const route = useRoute();
const subpage = ref('all');
const now = ref(new Date());
const subpageGradesShowDetail = ref(false);

const subpageGrades = () => {
  if (subpage.value !== 'grades') {
    subpage.value = 'grades';
    subpageGradesShowDetail.value = false;
  } else {
    subpageGradesShowDetail.value = !subpageGradesShowDetail.value;
  }
}

const exams = ref(DataModel.user?.exam?.subjects || []);

// 处理考试数据，添加状态和倒计时
const processedExams = computed(() => {
  return exams.value.map(exam => {
    // 从考试时间中提取开始时间部分
    const timePart = exam.考试安排.考试时间.split(' - ')[0];
    const examDate = new Date(timePart.replace(/-/g, '/'));
    const diffTime = examDate - now.value;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    let countdownText = '';
    let status = '';

    if (diffTime > 0) {
      status = 'upcoming';
      if (diffDays === 1) {
        countdownText = '明天';
      } else if (diffDays === 0) {
        countdownText = '今天';
      } else {
        countdownText = `${diffDays}天`;
      }
    } else {
      status = 'completed';
      const daysPassed = Math.floor(-diffTime / (1000 * 60 * 60 * 24));
      countdownText = daysPassed === 0 ? '今天' : `${daysPassed}天前`;
    }

    return {
      ...exam,
      examDate,
      countdownText,
      status
    };
  }).sort((a, b) => a.examDate - b.examDate);
});

// 过滤考试
const filteredExams = computed(() => {
  if (filter.value === 'all') return processedExams.value;
  return processedExams.value.filter(exam => exam.status === filter.value);
});

// 更新当前时间（每分钟更新一次）
onMounted(() => {
  setInterval(() => {
    now.value = new Date();
  }, 60000);
});
</script>

<style scoped>
.view-container {
  margin: 0;
  padding: 0;
}

/* #region 为空样式 */

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 50px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.empty-state i {
  font-size: 4rem;
  color: #bdc3c7;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #7f8c8d;
  margin-bottom: 15px;
}

/* #endregion */

/* #region 筛选按钮 */

.subpage-bar {
  position: fixed;
  bottom: 64px;
  width: 100%;
  left: 0;
  right: 0;
  padding: 10px;
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  padding: 10px 0;
  z-index: 100;
  margin-bottom: 0;
  background-image: linear-gradient(0deg, #fff7f7c0, #ffffff00);
}

.subpage-btn {
  padding: 12px 16px;
  background-color: rgba(220, 220, 220, 0.667);
  border-radius: 25px;
  border: 1px solid #6363637f;
  color: #555;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 0.9rem;
  white-space: nowrap;
  flex: 1;
  max-width: 30%;
  margin: 0 5px;
}

.subpage-btn.active {
  background: #3498db;
  color: white;
  border: none;
  transition: all ease 0.3s;
}

.subpage-btn.active[data-v-xxxxxx] {
  color: white;
}

.subpage-btn:first-child.active {
  background: linear-gradient(135deg, #3498db, #2980b9);
}

.subpage-btn:nth-child(2).active {
  background: linear-gradient(135deg, #f39c12, #e67e22);
}

.subpage-btn:last-child.active {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
}

/* #endregion */
</style>