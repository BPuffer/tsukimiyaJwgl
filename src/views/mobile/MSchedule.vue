<template>
  <!-- <p>selectedDate: {{ selectedDate }}</p>
  <p>currentMonday: {{ currentMonday }}</p>
  <p>isCurrentWeek: {{ isCurrentWeek }}</p> -->
  <div class="mobile-schedule-container">
    <!-- 二级导航 -->
    <div class="subpage-bar">
      <button class="subpage-btn" @click="prevWeek">
        <i class="fas fa-chevron-left"></i>
      </button>
      <button class="subpage-btn" @click="openDatePicker">
        <i class="fas fa-calendar"></i>日期
      </button>
      <button class="subpage-btn week-display-btn">
        {{ weekNumberText }}
      </button>
      <button class="subpage-btn" :class="{ 'current-week': isCurrentWeek }" @click="goToToday">
        <i class="fas fa-calendar-day"></i>本周
      </button>
      <button class="subpage-btn" @click="nextWeek">
        <i class="fas fa-chevron-right"></i>
      </button>
      <input ref="datePicker" type="date" v-model="selectedDate" style="display: none;">
    </div>

    <!-- 课程表 -->
    <div class="table-container">
      <table v-if="schedule !== null" class="schedule-table">
        <thead>
          <tr>
            <th>时间</th>
            <th v-for="(day, index) in weekDays" :key="index" :class="{ 'current-day': isCurrentDay(index) }">
              {{ day }}
              <div>{{ getDateString(index) }}</div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(timeSlot, timeIndex) in schedule.times" :key="timeIndex">
            <td class="time-cell">
              <div class="period">第{{ timeIndex + 1 }}节</div>
              <div class="time-range">{{ timeSlot[0] }}</div>
              <div class="time-range">{{ timeSlot[1] }}</div>
            </td>
            <!-- 空课表提示 -->
            <td class="all-schedule-empty-bigcell" v-if="allScheduleEmpty && !weekCourse && timeIndex === 0"
              :rowspan="schedule.times.length" :colspan="7">
              <div class="all-schedule-empty-tip">
                本周没有任何课程 <i class="fa-solid fa-mug-hot"></i>
              </div>
            </td>

            <!-- 全周课单元格 -->
            <td v-if="!allScheduleEmpty && showWeekCourse && timeIndex === 0" :ref="el => weekCourseRef = el"
              class="week-course-bigcell" :rowspan="schedule.times.length" :colspan="5" :style="{
                backgroundImage: stringToGradient(weekCourse.课程名称, 0, 0.2, radial = true)
              }">
              <div class="week-course-tip-container1">
                <div class="week-course-tip-container2" :style="{
                  backgroundImage: stringToGradient(weekCourse.课程名称)
                }">
                  <!--上课时间:"5-7周"
                  授课教师:"王茜"
                  课程名称:"劳动教育"
                  -->
                  <div class="week-course-tip-title">
                    {{ weekCourse.课程名称 }} <br>
                  </div>
                  授课教师: {{ weekCourse.授课教师 }} <br>
                  上课时间: {{ weekCourse.上课时间 }}
                </div>
              </div>
            </td>

            <!-- 普通课程单元格 -->
            <td class="course-td"
              v-for="([dayIndex, day]) in enumerate(showWeekCourse ? weekDays.slice(5) : weekDays, showWeekCourse ? 5 : 0)"
              v-if="!allScheduleEmpty" :key="dayIndex" :class="{ 'empty-td': !getCourse(dayIndex, timeIndex) }">
              <div class="course-limitbox">
                <div v-if="getCourse(dayIndex, timeIndex)" class="course-card"
                  @click="openCourseDrawer(getCourse(dayIndex, timeIndex))"
                  :style="{ backgroundImage: stringToGradient(getCourse(dayIndex, timeIndex).课程名称) }">
                  <h3 class="course-name">
                    {{ getCourse(dayIndex, timeIndex).课程名称 }}
                  </h3>
                  <div class="course-location">
                    {{ getCourse(dayIndex, timeIndex).上课地点 }}
                  </div>
                  <div class="course-teacher">
                    {{ getCourse(dayIndex, timeIndex).授课教师 }}
                  </div>
                  <!-- <div class="course-details">
                    <h3>{{ getCourse(dayIndex, timeIndex).课程名称 }}</h3>
                    <p><i class="fas fa-map-marker-alt"></i> {{ getCourse(dayIndex, timeIndex).上课地点 }}</p>
                    <p><i class="fas fa-star"></i> {{ getCourse(dayIndex, timeIndex).课程学分 }}</p>
                    <p><i class="fas fa-tag"></i> {{ getCourse(dayIndex, timeIndex).课程属性 }}</p>
                    <p><i class="fas fa-clock"></i> {{ getCourse(dayIndex, timeIndex).上课时间 }}</p>
                  </div> -->
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 抽屉组件 -->
    <div v-if="drawerVisible" class="drawer-mask" @click="closeDrawer">
      <div class="drawer" @click.stop>
        <div class="drawer-header">
          <h2>{{ activeCourse.课程名称 }}</h2>
          <button class="close-btn" @click="closeDrawer">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="drawer-content">
          <div class="info-grid">
            <div class="info-item">
              <label>上课地点</label>
              <span>{{ activeCourse.课程名称 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>课程学分</label>
              <span>{{ activeCourse.上课地点 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>课程属性</label>
              <span>{{ activeCourse.上课时间 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>上课时间</label>
              <span>{{ activeCourse.授课教师 || '-' }}</span>
            </div>
          </div>
          <div class="drawer-sentinel"></div>
        </div>
      </div>
    </div>

    <!-- 完全课表隐藏组件，用于学习通识别导入 -->
    <div style="display: none;" v-html="scheduleAll"></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, warn, onMounted, onUnmounted, nextTick } from 'vue';
import Hammer from 'hammerjs'
import DataModel from '@/models/DataModel';
const schedule = ref(DataModel.user?.schedule || { "nope": 1 });
const scheduleAll = ref(schedule.value.all);

const weekDays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
const weekDayKeys = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];

// 当前日期处理
const today = new Date();
const todayMonday = calculateMonday(today);
const selectedDate = ref(formatDate(today));
const currentMonday = ref(calculateMonday(today));
watch(selectedDate, (newDate) => {
  currentMonday.value = calculateMonday(new Date(newDate));
});

onMounted(() => {
  if (showWeekCourse.value) {
    initHammer();
  }
});
onUnmounted(() => {
  destroyHammer();
});

// #region 初始属性
const weekNumberText = computed(() => {
  const weekStr = getWeekNumber();
  return weekStr.replace(/[()]/g, '') || '学期外';
});

const isCurrentWeek = computed(() => {
  return formatDateYYYYMMDD(todayMonday) === formatDateYYYYMMDD(currentMonday.value);
});
// #endregion

// #region 特殊标记 完全没有课程和全周(实习)课程
const hideWeekCourse = ref(false);
const allScheduleEmpty = computed(() => {
  const weekData = getDateWeekCourses(new Date(currentMonday.value))
  const hasWeekCourse = weekData && "week_course" in weekData;
  if (hasWeekCourse) return false;
  const weekSchedules = weekData?.schedules;
  if (!weekSchedules) return true;
  for (const dayKey in weekSchedules) {
    if (weekSchedules[dayKey].length > 0) return false;
  }
  return true;
});
const onWeekCourseHide = () => {
  hideWeekCourse.value = true;
};
const onWeekCourseReset = () => {
  hideWeekCourse.value = false;
};
const weekCourse = computed(() => {
  return getDateWeekCourses(new Date(currentMonday.value))?.week_course;
});
const showWeekCourse = computed(() => {
  return Boolean(weekCourse.value) && (!hideWeekCourse.value);
});

// 长按事件处理
const hammerManager = ref(null);
const isLongPress = ref(false);
const weekCourseRef = ref(null);
const initHammer = () => {
  if (weekCourseRef.value && !hammerManager.value) {
    hammerManager.value = new Hammer(weekCourseRef.value);
    hammerManager.value.get('press').set({ time: 500 });

    hammerManager.value.on('press', () => {
      isLongPress.value = true;
      onWeekCourseHide();
    });

    hammerManager.value.on('pressup', () => {
      setTimeout(() => { isLongPress.value = false }, 100);
    });
  }
};
const destroyHammer = () => {
  if (hammerManager.value) {
    hammerManager.value.destroy();
    hammerManager.value = null;
  }
};
watch(showWeekCourse, (newVal) => {
  if (newVal) {
    // 等待 DOM 更新后初始化
    nextTick(() => {
      initHammer();
    });
  } else {
    destroyHammer();
  }
});
// #endregion

// #region 第？周
function getWeekNumber() {
  const mondayStr = formatDateYYYYMMDD(new Date(currentMonday.value));
  if (schedule.value.mondays && mondayStr in schedule.value.mondays) {
    return `(第${schedule.value.mondays[mondayStr].week}周)`
  }
  return '';
}

function getDateWeekCourses(date) {
  const mondayStr = formatDateYYYYMMDD(date);
  if (schedule.value.mondays) { return schedule.value.mondays[mondayStr]; }
  return '';
}

function getCourse(dayIndex, timeIndex) {
  const weekSchedules = getDateWeekCourses(new Date(currentMonday.value))?.schedules;
  if (!weekSchedules) return null;
  const dayKey = weekDayKeys[dayIndex];
  const daySchedule = weekSchedules[dayKey];
  if (!daySchedule || daySchedule.length <= timeIndex) return null;
  return daySchedule[timeIndex];
}
// #endregion

// #region 课程颜色
function stringToGradient(str, sA = 0.9, eA = 0.5, radial = false) {
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
    hash ^= hash >> 13n;
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
    else[r, g, b] = [c, 0, x];
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
  const diff_ = parseInt(seed / 10000) % 80 - 40;
  const diff = diff_ > 0 ? diff_ + 30 : diff_ - 30;

  const sH = seed % 360, sS = 95, sV = 70 + seed % 20
  const startColor = toColorString(sH, sS, sV, sA);

  const eH = (sH + diff) % 360, eS = 95, eV = 70 + parseInt(seed / 100) % 20;
  const endColor = toColorString(eH, eS, eV, eA);
  return radial
    ? `radial-gradient(circle, ${startColor} 0%, ${endColor} 100%)`
    : `linear-gradient(135deg, ${startColor}, ${endColor})`;
}
// #endregion

// #region 抽屉
const drawerVisible = ref(false);
const activeCourse = ref(null);

function openCourseDrawer(course) {
  activeCourse.value = course;
  drawerVisible.value = true;
}

function closeDrawer() {
  drawerVisible.value = false;
}
// #endregion

// #region 操作函数
function prevWeek() {
  onWeekCourseReset();
  const date = new Date(currentMonday.value);
  date.setDate(date.getDate() - 7);
  currentMonday.value = date;
  selectedDate.value = formatDate(date);
}

function nextWeek() {
  onWeekCourseReset();
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

function openDatePicker() {
  const datePicker = document.querySelector('input[type="date"]');
  if (datePicker) {
    datePicker.showPicker();
  }
}
// #endregion

// #region 工具函数
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

function enumerate(array, start = 0) {
  return array.map((value, index) => [index + start, value]);
}

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
// #endregion

</script>

<style scoped>
/* #region 基础容器 */
.mobile-schedule-container {
  width: 100%;
  overflow: hidden;
  padding: 0;
  position: relative;
  min-height: calc(100vh - 100px);
}

/* #endregion */

/* #region 额吉导航 */
.subpage-bar {
  position: fixed;
  bottom: 64px;
  height: 36px;
  width: 100%;
  left: 0;
  right: 0;
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

.subpage-btn i {
  font-size: 1rem;
}

.week-display-btn {
  flex: 1.5;
  font-weight: bold;
  background-color: rgba(200, 200, 240, 0.8);
  border: none;
}

/* #endregion */

/* #region 表格 */
/* 容器 */
.table-container {
  height: calc(100vh - 136px);
  max-width: 100%;
  overflow-x: auto;
  margin-top: 10px;
}

.schedule-table {
  height: calc(100vh - 136px);
  table-layout: fixed;
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background-clip: padding-box;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.schedule-table th,
.schedule-table td {
  width: 12.5%;
}

/* #region 表头 */
.schedule-table th {
  background: #f8f9fcc0;
  background-clip: padding-box;
  padding: 12px 5px;
  text-align: center;
  font-weight: 600;
  color: #4a5568;
  border: 1px solid transparent;
  width: 12.5%;
  font-size: 0.85rem;
  min-height: 50px;
  max-height: 50px;
}

/* #endregion */

/* #region 课程格和卡片 */
.schedule-table td {
  border: 1px solid transparent;
  vertical-align: top;
  background-clip: padding-box;
}

.course-td {
  max-height: 100%;
  background: #f8fafc20;
}

.empty-td {
  background: #f8fafc50;
}

.course-limitbox {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: calc((100vh - 136px - 50px) / 5);
  overflow: auto;
}

.course-card {
  height: 100%;
  max-height: 100%;
  box-sizing: border-box;
  padding: 8px;
  border-radius: 8px;
  color: white;
}

.course-name {
  font-weight: 600;
  font-size: 0.85rem;
  margin: 0;
  margin-bottom: 2px;
  line-height: 1.2;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4;
  overflow: hidden;
}

.course-location {
  font-size: 0.75rem;
  margin: 0;
  /* margin-bottom: 2px; */
  line-height: 1;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  opacity: 0.9;
}

.course-teacher {
  font-size: 0.75rem;
  margin: 0;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  overflow: hidden;
  opacity: 0.9;
}

/* #endregion */

/* #region 表列头 */
.time-cell {
  background-color: #f8f9fcc0;
  text-align: center;
  padding: 5px;
  font-weight: 500;
  color: #4a5568;
  position: relative;
  font-size: 0.8rem;
  height: 20%;
}

.time-cell .period {
  font-size: 0.9rem;
  color: #697c97;
}

.time-cell .time-range {
  font-size: 0.75rem;
  margin-top: 3px;
  color: #8ca3c2;
}

/* #endregion */

/* #endregion */

/* #region 特殊标记 */
/* 今天按钮本周高亮 */
.current-week {
  background-color: #4caf50;
  color: #fff;
}

/* 表头今天高亮 */
.schedule-table th.current-day {
  background: #1976d2;
  background-clip: padding-box;
  border: 1px solid transparent;
  color: #e3f2fd;
}

/* 本周没有课程 */
.all-schedule-empty-bigcell {
  text-align: center;
  vertical-align: middle;
  width: 100%;
  height: 100%;
  background-color: #fff7;
}

.all-schedule-empty-tip {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  height: 75%;
}

/* 全周课程 */
.week-course-bigcell td {
  text-align: center;
  vertical-align: middle;
  width: 67.5%;
  /* background: radial-gradient(circle, #e2ffde20 0%, #93ff85c0 100%); */
  border-radius: 10px;
  height: 100%;
}

.week-course-tip-container1 {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  text-align: left;
  height: 100%;
  color: white;
}

.week-course-tip-container2 {
  text-align: left;
  color: white;
  padding: 10px;
  border-radius: 10px;
  font-size: 1.1em;
  min-width: 75%;
}

.week-course-tip-title {
  font-size: 1.2em;
  font-weight: 600;
  text-align: center;
  padding-bottom: 5px;
  border-bottom: 1px solid #fff;
  margin-bottom: 5px;
}

/* #endregion */

/* #region 详情抽屉 */
/* 抽屉样式 */
.drawer-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  animation: fadeIn 0.3s ease;
}

.drawer {
  background: white;
  width: 100%;
  border-radius: 20px 20px 0 0;
  max-height: 50vh;
  overflow-y: auto;
  transform: translateY(0);
  transition: transform 0.3s ease;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
}

.drawer-header h2 {
  margin: 0;
  font-size: 1.4rem;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #7f8c8d;
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #f5f7fa;
  color: #e74c3c;
}

.drawer-content {
  padding: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item label {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 5px;
}

.info-item span {
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 500;
}

.drawer-sentinel {
  height: 5vh;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

/* #endregion */

/* #region 响应式调整 */
@media (max-width: 480px) {
  .schedule-header {
    padding: 12px 15px 8px;
  }

  .title-section h1 {
    font-size: 1.2rem;
  }

  .subpage-btn {
    padding: 10px 12px;
    font-size: 0.8rem;
  }

  .schedule-table th {
    font-size: 0.75rem;
    padding: 8px 3px;
  }

  .time-cell {
    width: 60px;
    font-size: 0.75rem;
    padding: 4px;
  }

  .time-cell .period {
    font-size: 0.8rem;
  }

  .time-cell .time-range {
    font-size: 0.7rem;
  }

  .course-card {
    padding: 6px;
  }

  .course-name {
    font-size: 0.75rem;
  }

  .course-location {
    font-size: 0.65rem;
  }

  .course-details {
    padding: 6px;
    font-size: 0.7rem;
  }

  .course-details h3 {
    font-size: 0.85rem;
  }

  .course-details p {
    font-size: 0.65rem;
  }
}

@media (max-width: 360px) {
  .schedule-table td {
    height: 75px;
  }

  .course-name {
    font-size: 0.7rem;
  }

  .course-location {
    font-size: 0.6rem;
  }
}

/* #endregion */
</style>