<template>
  <div class="schedule-container">
    <div class="schedule-header">
      <div class="title-section">
        <h1>我的课程表 <span v-if="isCurrentWeek" class="current-week">本周</span></h1>
        <p v-if="schedule===null" style="color: red;">暂时没有课程表</p>
      </div>
      <div v-if="schedule!==null" class="date-controls">
        <div class="week-nav">
          <button class="nav-button" @click="prevWeek">
            <i class="fas fa-chevron-left"></i>
          </button>
          <div class="week-display">
            {{ displayWeekRange }}
          </div>
          <button class="nav-button" @click="nextWeek">
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
        <input type="date" class="date-picker" v-model="selectedDate">
        <button class="today-button" @click="goToToday">
          <i class="fas fa-calendar-day"></i> 今天
        </button>
      </div>
    </div>
    
    <table v-if="schedule!==null" class="schedule-table">
      <thead>
        <tr>
          <th>时间</th>
          <th v-for="(day, index) in weekDays" :key="index" 
              :class="{ 'current-day': isCurrentDay(index) }">
            {{ day }}
            <span>{{ getDateString(index) }}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(timeSlot, timeIndex) in schedule.times" :key="timeIndex">
          <td class="time-cell">
            <div class="period">第{{ timeIndex + 1 }}大节</div>
            <div class="time-range">{{ timeSlot[0] }} - {{ timeSlot[1] }}</div>
          </td>
          <td v-for="(day, dayIndex) in weekDays" :key="dayIndex" class="course-cell"
              :class="{ 'empty-cell': !getCourse(dayIndex, timeIndex) }">
            <div v-if="getCourse(dayIndex, timeIndex)" class="course-card"
                :style="{backgroundImage: stringToGradient(getCourse(dayIndex, timeIndex).课程名称)}">
              <h3 class="course-name">
                {{ getCourse(dayIndex, timeIndex).课程名称 }}
              </h3>
              <div class="course-location">
                {{ getCourse(dayIndex, timeIndex).上课地点 }}
              </div>
              <div class="course-details">
                <h3>{{ getCourse(dayIndex, timeIndex).课程名称 }}</h3>
                <p><i class="fas fa-map-marker-alt"></i> {{ getCourse(dayIndex, timeIndex).上课地点 }}</p>
                <p><i class="fas fa-star"></i> {{ getCourse(dayIndex, timeIndex).课程学分 }}</p>
                <p><i class="fas fa-tag"></i> {{ getCourse(dayIndex, timeIndex).课程属性 }}</p>
                <p><i class="fas fa-clock"></i> {{ getCourse(dayIndex, timeIndex).上课时间 }}</p>
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    
    </table>
  </div>
</template>

<script setup>
import { ref, computed, watch, warn, onMounted } from 'vue';
import DataModel from '@/models/DataModel';
const schedule = ref(DataModel.user?.schedule || {"nope": 1});

const weekDays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
const weekDayKeys = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];

// 当前日期处理
const today = new Date();
const selectedDate = ref(formatDate(today));
const currentMonday = ref(calculateMonday(today));

// 计算属性
const displayWeekRange = computed(() => {
  const monday = new Date(currentMonday.value);
  const sunday = new Date(monday);
  sunday.setDate(monday.getDate() + 6);
  
  const m = `${monday.getMonth() + 1}月${monday.getDate()}日`;
  const s = `${sunday.getMonth() + 1}月${sunday.getDate()}日`;
  return `${m} - ${s} ${getWeekNumber()}`;
});

const isCurrentWeek = computed(() => {
  const todayMonday = calculateMonday(new Date());
  return todayMonday.toISOString().slice(0, 10) === 
         new Date(currentMonday.value).toISOString().slice(0, 10);
});

// 监听日期变化
watch(selectedDate, (newDate) => {
  currentMonday.value = calculateMonday(new Date(newDate));
});

// 第？周
function getWeekNumber() {
  const mondayStr = formatDateYYYYMMDD(new Date(currentMonday.value));
  // const weekData = ;
  if (schedule.value.mondays && mondayStr in schedule.value.mondays) {
    return `(第${schedule.value.mondays[mondayStr].week}周)`
  }
  return '';
}

function getCourse(dayIndex, timeIndex) {
  const mondayStr = formatDateYYYYMMDD(new Date(currentMonday.value));
  const weekData = schedule.value.mondays[mondayStr];
  
  if (!weekData || !weekData.schedules) return null;
  
  const dayKey = weekDayKeys[dayIndex];
  const daySchedule = weekData.schedules[dayKey];
  
  if (!daySchedule || daySchedule.length <= timeIndex) return null;
  
  return daySchedule[timeIndex];
}

// 课程颜色
function stringToGradient(str, sA = 0.9, eA = 0.5) {
  function hashCode(str) {
    let hash = 0n;
    const prime = 1099511628211n;
    const mod = 2n ** 64n;
    for (let i = 0; i < str.length; i++) {
        hash = (hash * prime + BigInt(str.charCodeAt(i))) % mod;
        hash = (hash << 13n) | (hash >> (64n - 13n));
    }
    hash ^= hash >> 20n;
    hash ^= hash << 41n;
    hash ^= hash >> 14n;
    return Number(hash % 2n ** 32n) | 0;
}
  function hsvToRgba(h, s, v, a = 1) {
    h = (h % 360) / 60;
    s /= 100;
    v /= 100;
    const c = v * s;
    const x = c * (1 - Math.abs(h % 2 - 1));
    let r, g, b;
    if (0 <= h && h < 1) [r, g, b] = [c, x, 0];
    else if (1 <= h && h < 2) [r, g, b] = [x, c, 0];
    else if (2 <= h && h < 3) [r, g, b] = [0, c, x];
    else if (3 <= h && h < 4) [r, g, b] = [0, x, c];
    else if (4 <= h && h < 5) [r, g, b] = [x, 0, c];
    else [r, g, b] = [c, 0, x];
    r = Math.round((r + v - c) * 255);
    g = Math.round((g + v - c) * 255);
    b = Math.round((b + v - c) * 255);
    return [r, g, b, a];
  }
  function toColorString(h, s, v, a) {
    const rgba = hsvToRgba(h, s, v, a);
    return a === 1 
      ? `#${[r, g, b].map(c => c.toString(16).padStart(2, '0')).join('')}`
      : `rgba(${rgba[0]}, ${rgba[1]}, ${rgba[2]}, ${rgba[3]})`;
  }
  const seed = Math.abs(hashCode(str));
  const diff_ = seed % 80 - 40;
  const diff = diff_ > 0 ? diff_ + 30 : diff_ - 30;

  const sH = seed % 360, sS = 95, sV = 70 + seed % 20
  const startColor = toColorString(sH, sS, sV, sA);

  const eH = (sH + diff) % 360, eS = 95, eV = 70 + parseInt(seed / 1000) % 20;
  const endColor = toColorString(eH, eS, eV, eA);
  return `linear-gradient(135deg, ${startColor}, ${endColor})`;
}

// 操作函数
function getDateString(dayIndex) {
  const monday = new Date(currentMonday.value);
  const date = new Date(monday);
  date.setDate(monday.getDate() + dayIndex);
  return `${date.getMonth() + 1}/${date.getDate()}`;
}

function isCurrentDay(dayIndex) {
  const today = new Date();
  const monday = new Date(currentMonday.value);
  const date = new Date(monday);
  date.setDate(monday.getDate() + dayIndex);
  return date.toDateString() === today.toDateString();
}

function prevWeek() {
  const date = new Date(currentMonday.value);
  date.setDate(date.getDate() - 7);
  currentMonday.value = date;
  selectedDate.value = formatDate(date);
}

function nextWeek() {
  const date = new Date(currentMonday.value);
  date.setDate(date.getDate() + 7);
  currentMonday.value = date;
  selectedDate.value = formatDate(date);
}

function goToToday() {
  const today = new Date();
  currentMonday.value = calculateMonday(today);
  selectedDate.value = formatDate(today);
}

// 工具函数
function calculateMonday(date) {
  const day = date.getDay();
  const diff = date.getDate() - day + (day === 0 ? -6 : 1);
  return new Date(date.setDate(diff));
}

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatDateYYYYMMDD(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}${month}${day}`;
}
</script>

<style scoped>
/* #region 整体容器 */
.schedule-container {
  width: 95%;
  max-width: 1400px;
  border-radius: 20px;
  box-shadow: 0 15px 50px rgba(0, 0, 150, 0.15);
  overflow: hidden;
  margin: 20px auto;
}
/* #endregion */

/* #region 头 */
.schedule-header {
  background: linear-gradient(120deg, #2c3e50, #4a6491);
  color: white;
  padding: 25px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.title-section h1 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 5px;
}

.title-section p {
  opacity: 0.85;
  font-size: 15px;
}
/* #endregion */

/* #region 控件 */
.date-controls {
  display: flex;
  gap: 15px;
  align-items: center;
}

.week-nav {
  display: flex;
  gap: 10px;
  align-items: center;
}

.week-display {
  background: rgba(255, 255, 255, 0.15);
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 500;
  min-width: 240px;
  text-align: center;
}

.date-picker {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  padding: 10px 15px;
  border-radius: 8px;
  color: white;
  font-size: 15px;
  outline: none;
  cursor: pointer;
}

.date-picker::-webkit-calendar-picker-indicator {
  filter: invert(1);
  cursor: pointer;
}

.nav-button {
  background: #ffffff26;
  border: none;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-button:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.1);
}

.today-button {
  background: #38ada9;
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.today-button:hover {
  background: #079992;
}
/* #endregion */

/* #region 课表表格 */
/* 课表表格 */
.schedule-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  min-width: 1000px;
  background-clip: padding-box;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

/* 表头 */
.schedule-table th {
  background: #f8f9fcc0;
  background-clip: padding-box;
  padding: 15px 10px;
  text-align: center;
  font-weight: 600;
  color: #4a5568;
  border: 2px solid transparent;
  /* position: sticky; */
  top: 0;
  z-index: 10;
}

/* 表格 */
.schedule-table td {
  border: 2px solid transparent;
  height: 100px;
  width: 12.5%;
  vertical-align: top;
  background-clip: padding-box;
}

/* 表列头 */
.time-cell {
  background: #f8f9fcc0;
  text-align: center;
  padding: 5px;
  font-weight: 500;
  color: #4a5568;
  position: relative;
}

.time-cell .period {
  font-size: 1.2em;
  color: #697c97;
}

.time-cell .time-range {
  font-size: 1em;
  margin-top: 3px;
  color: #8ca3c2;
}

/* 课程 */
.empty-cell {
  background: #f8fafcc0;
}

.course-cell {
  background: rgba(255, 255, 255, 0.1);
}
/* #endregion */

/* #region 课程卡片 */
.course-card {
  height: 100%;
  box-sizing: border-box;
  padding: 10px;
  border-radius: 8px;
  /* background: #7777; */
  color: white;
  transition: all 0.3s ease;
  box-shadow: 0 3px 10px rgba(74, 105, 189, 0.2);
  position: relative;
  overflow: hidden;
  cursor: cell;
}

.course-card:hover {
  box-shadow: 0 5px 15px rgba(74, 105, 189, 0.4);
}

.course-location {
  font-size: 13px;
  opacity: 0.9;
}

.course-details {
  box-sizing: border-box;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(42, 50, 75, 0.95);
  padding: 10px;
  border-radius: 8px;
  color: white;
  opacity: 0;
  transition: all 0.4s ease;
  pointer-events: none;
  z-index: 10;
}

.course-card:hover .course-details {
  opacity: 1;
}

.course-details p {
  font-size: 12px;
  margin: 0;
  line-height: 1;
}

.course-name {
  font-weight: 600;
  font-size: 15px;
  margin-top: 0;
  margin-bottom: 5px;
}

.course-details h3 {
  margin-top: 0;
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 5px;
}
/* #endregion */

/* #region 本周、当天 */
.current-week {
  display: inline-block;
  background: #4caf50;
  color: white;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-left: 8px;
}

.schedule-table th.current-day {
  background: #1976d2;
  background-clip: padding-box;
  border: 2px solid transparent;
  color: #e3f2fd;
}
/* #endregion */
</style>