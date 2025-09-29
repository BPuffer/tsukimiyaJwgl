<template>
  <div class="bonus-view-container">
    <div v-if="eventsLoading" class="events-loading">
      <div class="loading-spinner"></div>
      <div class="loading-text">服务器可能又挂了...</div>
    </div>
    <!-- <div v-if="currentEvent" class="current-event">
      <h2 class="current-title">{{ currentEvent.title }}</h2>
      <div class="current-date">{{ currentEvent.date_tag }}</div>
      <div class="current-description">
        <div v-html="renderedDescription" class="markdown-content"></div>
        <div class="current-description-sentinel"></div>
      </div>
    </div> -->
    <MEvent :event="currentEvent" />
    <!-- <p>displayedEvents: {{ displayedEvents }}</p>
    <div v-if="displayedEvents.length > 0">
      <div v-for="(event, index) in displayedEvents">
        <button @click="console.debug(event)">{{event.title}}</button>
      </div>
    </div> -->
    <div v-if="!eventsLoading" class="nav-circle-container">
      <div class="nav-circle" ref="navCircleRef" @touchstart.passive="onDragStart" @touchmove.passive="onDragMove"
        @touchend="onDragEnd" :class="{ 'nav-circle-dragging': isDragging }">
        <div v-for="(event, index) in displayedEvents">
          <div class="nav-point" :key="index" :class="{ active: event?.title === currentEvent?.title, }"
            :style="calculatePointPositionStyle(index)">
            <div class="nav-label">{{ event.title }}</div>
          </div>
        </div>
        <div class="button-myscore" @click="openMyscore">
          <img src="@/assets/img/chest-closed.png" alt="我的分数">
        </div>
      </div>
    </div>
    <!-- <button @click="console.log(sortedEvents, displayedEvents)">测试</button> -->
    <!-- <p>rotationDelta: {{ rotationDelta }}</p> -->
    <!-- <p>rotationFix: {{ rotationFix }}</p> -->
    <!-- <p>fingerRelativeAngle: {{ fingerRelativeAngle }}</p> -->
    <!-- <p>isDragging: {{ isDragging }}</p> -->
    <!-- <p>dragStartAngle: {{ dragStartAngle }}</p> -->
    <!-- <p>fingerX: {{ fingerX }}</p> -->
    <!-- <p>fingerY: {{ fingerY }}</p> -->
    <!-- <p>navCircleRef: {{ navCircleRef }}</p> -->
    <!-- <p>fingerRelativeSqrDist: {{ fingerRelativeSqrDist }}</p> -->
    <!-- <p>currentIndex: {{ currentIndex }}</p> -->
    <!-- <p>currentEvent.title: {{ currentEvent?.title }}</p> -->
    <!-- <p>|fingerRelativeAngle-dragStartAngle|: {{ Math.abs(fingerRelativeAngle - dragStartAngle) }}</p> -->
    <!-- <p>showMyscore: {{ showMyscore }}</p> -->

    <!-- <p>debug: {{ debugmount }}</p> -->
    <div v-if="showMyscore" class="msmod-mask">
      <div class="msmod-modal">
        <div class="msmod-header">
          <div class="msmod-title-container">
            <h3 v-if="!totalScore">第二课堂分数计算器</h3>
            <h3 v-else>当前成绩：{{ totalScore.toFixed(2) }}</h3>
          </div>
          <div class="msmod-navigator">
            <button class="msmod-navigator-btn" @click="msmodSection = 'navigator'" :class="{
              'msmod-navigator-btn-active': msmodSection === 'navigator'
            }">输入导航</button>
            <button class="msmod-navigator-btn" @click="msmodSection = 'score'" :class="{
              'msmod-navigator-btn-active': msmodSection === 'score'
            }">成绩</button>
            <button class="msmod-navigator-btn" @click="msmodSection = 'manual'" :class="{
              'msmod-navigator-btn-active': msmodSection === 'manual'
            }">手动</button>
          </div>

        </div>
        <div class="msmod-body">
          <div v-if="msmodSection === 'navigator'" class="msmod-body-container">
            <div class="msmod-v-selections">
              <div class="msmod-v-selections" style="width: 100%;">
                <div class="msmod-term-title-container">
                  <button class="msmod-btn" @click="updateTerm(-1)" style="transform: rotate(90deg);">▼</button>
                  <div class="msmod-term-title">{{ currentTerm }}</div>
                  <button class="msmod-btn" @click="updateTerm(1)" style="transform: rotate(-90deg);">▼</button>
                </div>
                <div class="msmod-term-description">
                  <span style="font-weight: bold;">{{ currentTermData.source }}</span><br>
                  <div style="white-space: pre-line;">{{ currentTermData.description }}</div>
                </div>
                <div class="msmod-v-selections msmod-term-name-input-container">
                  <p class="msmod-form-label msmod-no-margin">输入项目名称：</p>
                  <input v-model="termNameInput" type="text" class="msmod-form-input"
                    :placeholder="currentTermData.suggest || '输入项目名称'" style="width: 100%;">
                </div>
                <div class="msmod-h-selections">
                  <div v-if="termItems.length > 0 && termItems[0].options.length > 0"
                    class="msmod-h-selections msmod-selection-interface-container">
                    <div v-for="(item, index) in termItems" :key="item.id" class="msmod-term-mapping-item">
                      <div v-if="item.options.length > 0" class="msmod-term-mapping-item-content">
                        <select class="msmod-form-select" v-model="selectedOptions[index]"
                          @change="updateSelected(index)">
                          <option value="请选择..." selected style="display: none;">请选择...</option>
                          <option v-for="option in item.options" :value="option">{{ option }}</option>
                        </select>
                      </div>
                    </div>
                  </div>
                  <div v-if="currentScore !== null" class="msmod-term-mapping-item">
                    <div class="msmod-term-mapping-item-content">
                      <button class="msmod-btn msmod-btn-accept" @click="addScore">提交({{ currentScore }}分)</button>
                    </div>
                  </div>
                  <div class="msmod-h-selections"
                    v-else-if="currentScore === null && termItems && termItems[termItems.length - 1]?.options?.length === 0">
                    <div class="msmod-term-mapping-item-content" style="width: 100%;justify-content: space-between;">
                      <input class="msmod-form-input" type="number" v-model="manualScore" placeholder="输入分数"
                        step="0.01">
                      <button class="msmod-btn msmod-btn-accept" @click="addManualScore"
                        style="width: 100%;">提交</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="msmodSection === 'manual'" class="msmod-body-container">
            <h2>成绩：<span id="msmod-score-total">{{ totalScore.toFixed(2) }}</span></h2>
            <div style="display: flex; flex-direction: column; justify-content: center;">
              <div class="msmod-v-selections">
                <p class="msmod-no-margin">手动添加规则：</p>
                <input v-model="manualName" class="msmod-form-input" placeholder="项目名称" />
                <input v-model="manualScoreInput" class="msmod-form-input" placeholder="项目成绩" />
                <button class="msmod-btn msmod-btn-accept" @click="addManualItem">添加</button>
              </div>
              <label class="msmod-error-hint">{{ errorHint }}</label>
            </div>
          </div>

          <div v-if="msmodSection === 'score'" class="msmod-body-container">
            <table>
              <thead>
                <tr>
                  <th>项目</th>
                  <th>成绩</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(score, index) in scores" :key="index" class="msmod-score-item">
                  <td>{{ score.name }}</td>
                  <td>{{ score.score.toFixed(2) }}</td>
                  <td>
                    <button class="msmod-delete-project" @click="removeScore(index)">删除</button>
                  </td>
                </tr>
                <tr v-if="scores.length === 0" id="msmod-no-scores">
                  <td colspan="3">还没有成绩……</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="msmod-footer">
          <div class="msmod-footer-hint-container">
            <p>* 警告：本工具仅在本地运行，不会上传任何数据，第二课堂分数及证明材料需要自行报备，本工具仅作为记录用途，最终分数请以官方文章和校方认定为准。</p>
          </div>
          <div class="msmod-footer-btn-container msmod-h-selections">
            <button class="msmod-footer-btn msmod-btn" @click="closeModal">取消</button>
            <button class="msmod-footer-btn msmod-btn-accept" @click="savequit">保存</button>
          </div>
        </div>
      </div>
    </div>
    <!-- <p>msmodSection: {{ msmodSection }}</p> -->
    <!-- <p>selectedOptions: {{ selectedOptions }}</p> -->
    <!-- <p>currentTermIndex: {{ currentTermIndex }}</p> -->
    <!-- <p>currentTerm: {{ currentTerm }}</p> -->
    <!-- <p>currentTermData: {{ currentTermData }}</p> -->
    <!-- <p>termItems: {{ termItems }}</p> -->
    <!-- <p>termItems[0]?.options?.length: {{ termItems[0]?.options?.length }}</p> -->
    <!-- <p>null: {{ null }}</p> -->

    <!-- <p>events: {{ events }}</p> -->
  </div>
</template>

<script setup>
import { ref, computed, watch, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router';
import DataModel from '@/models/DataModel';
import MEvent from '@/components/MEvent.vue';
import { marked } from 'marked';
import '@/assets/markdown-styles.css';

const router = useRouter();
const eventsLoading = ref(true);
const events = ref({});

const loadEvent = () => {
  if (Object.keys(DataModel.server?.events).length === 0) {
    events.value = {
      "_placeholder": {
        "title": "暂无活动",
        "description": "暂无活动",
        "date_tag": "-",
        "timestamp": "0",
        "prevImg": "/img/exam_unknown_thumb.png",
        "bgImg": "/img/military_bg.jpg"
      }
    }
  } else {
    events.value = {
      ...DataModel.server?.events,
    }
  }
  eventsLoading.value = false;
}


const renderedDescription = computed(() => {
  return marked.parse(currentEvent.value.description)
})


// #region 导航环初始化
const mainItemAngle = -155;
const subItemIntervalAngle = 20;
const sortedEvents = computed(() => {
  // 按报名开始日期排序
  return Object.values(events.value).sort((a, b) => {
    return Number(a.timestamp) - Number(b.timestamp)
  })
})
// 总活动数量
const eventsLength = computed(() => {
  return Object.keys(events.value).length;
})
// 当前显示的活动。初始化。
const currentIndex = ref(5)  // 后面换成时间检查
// 当前活动详情，用于主文档显示
const currentEvent = computed(() => {
  const index = (currentIndex.value + 5 * eventsLength.value) % eventsLength.value
  return sortedEvents.value[index]
})

// 当前显示的活动前取5个后取5个，循环显示
const displayedEvents = computed(() => {
  if (eventsLength.value === 0) {
    throw new Error("不预期的错误：活动数量为0。没有活动时应该有一个默认的占位符。")
  }
  return Array.from({ length: 11 }, (_, i) => {
    return (currentIndex.value + (i - 5) + eventsLength.value * 5) % eventsLength.value;
  })
    .map(index => {
      if (sortedEvents.value[index] === undefined) {
        console.debug(`on displayedEvents, index: ${index}, eventsLength: ${eventsLength.value}, currentIndex: ${currentIndex.value}`)
      }
      return sortedEvents.value[index]
    })
})
// #endregion

// #region 导航环拖拽
const isDragging = ref(false)
const dragStartAngle = ref(0)
const rotationFix = ref(0)
// 拖拽时，记录旋转角度
const rotationDelta = computed(() => {
  if (!isDragging.value) {
    return 0
  }
  return fingerRelativeAngle.value - dragStartAngle.value + rotationFix.value
})

// 当角度超过subItemIntervalAngle°时索引+1并修正角度，反之反之。
watch(rotationDelta, (rotationDelta) => {
  if (rotationDelta > (subItemIntervalAngle / 2) + 1) {
    currentIndex.value = (currentIndex.value - 1 + eventsLength.value) % eventsLength.value;
    rotationFix.value -= subItemIntervalAngle;
  } else if (rotationDelta < -(subItemIntervalAngle / 2) - 1) {
    currentIndex.value = (currentIndex.value + 1) % eventsLength.value;
    rotationFix.value += subItemIntervalAngle;
  }
})
const navCircleRef = ref(null)  // ref引用导航圆本体
const fingerX = ref(NaN)
const fingerY = ref(NaN)
const fingerRelativeAngle = computed(() => {
  if (isNaN(fingerX.value) || isNaN(fingerY.value) || !navCircleRef.value) { return NaN }
  const rect = navCircleRef.value.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2
  return (Math.atan2(fingerY.value - centerY, fingerX.value - centerX) * 180 / Math.PI + 360) % 360
})
const fingerRelativeSqrDist = computed(() => {
  if (isNaN(fingerX.value) || isNaN(fingerY.value) || !navCircleRef.value) { return NaN }
  const rect = navCircleRef.value.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2
  return Math.pow(fingerX.value - centerX, 2) + Math.pow(fingerY.value - centerY, 2)
})

let setScrollTimeout = null  // 滚动锁延时释放

// 开始拖拽时
const onDragStart = (event) => {
  document.body.style.overflow = 'hidden'
  if (setScrollTimeout) {
    clearTimeout(setScrollTimeout)
  }
  // 激活手指位置
  const touch = event.touches[0]
  fingerX.value = touch.clientX
  fingerY.value = touch.clientY
  // 记录起始角度
  isDragging.value = true
  dragStartAngle.value = fingerRelativeAngle.value
}

const onDragMove = (event) => {
  if (!isDragging.value) return
  // 记录拖拽时角度
  const touch = event.touches[0]
  fingerX.value = touch.clientX
  fingerY.value = touch.clientY
}

const onDragEnd = () => {
  if (!isDragging.value) return
  isDragging.value = false
  rotationFix.value = 0
  setScrollTimeout = setTimeout(() => {
    document.body.style.overflow = 'auto'
  }, 300)

}

// #endregion

// #region 导航环维护
const circleRadius = ref(0)
const calculatePointPositionStyle = (index) => {
  // 计算每个点在圆上的位置
  // 当前活动在-165°，前面5个依次减少subItemIntervalAngle°，后面5个依次增加subItemIntervalAngle°
  const angle = mainItemAngle + (index - 5) * subItemIntervalAngle + rotationDelta.value
  const radians = angle * Math.PI / 180
  const radius = circleRadius.value
  const x = Math.cos(radians) * radius
  const y = Math.sin(radians) * radius

  return {
    left: `calc(50% + ${x}px)`,
    top: `calc(50% + ${y}px)`,
    backgroundImage: `url(${displayedEvents.value[index].prevImg})`,
    transition: isDragging.value ? 'none' : 'left 0.3s ease, top 0.3s ease'
  }
}
// #endregion

// #region 我的分数界面
import { ScoreModel } from '@/models/scoremodel.js';
import { scoreMappings } from '@/models/scoreMappings.js';
const msmodSection = ref('navigator')
const showMyscore = ref(false)
const scoreModel = ref(new ScoreModel());
function openMyscore() {
  scoreModel.value = new ScoreModel(DataModel.user?.client?.scores || DataModel?.visitor?.scores || []);
  showMyscore.value = true;
}

// #region 导航-输入导航
// 项目相关状态
const termNames = Object.keys(scoreMappings);
const currentTermIndex = ref(0);
const currentTerm = computed(() => termNames[currentTermIndex.value]);
const currentTermData = computed(() => scoreMappings[currentTerm.value]);

// 选项选择状态
const selectedOptions = ref([]);
const termItems = ref([]);
const termNameInput = ref('');
const currentScore = ref(null);
const currentLevelIsObject = ref(false);
// 左右按钮激活当前项目
function updateTerm(delta) {
  currentTermIndex.value = (currentTermIndex.value + delta + termNames.length) % termNames.length;
  resetTermSelection();
}
function resetTermSelection() {
  selectedOptions.value = [];
  updateTermItems();
}


function updateSelected(index) {
  // 截断到当前索引
  selectedOptions.value = selectedOptions.value.slice(0, index + 1);
  updateTermItems();
}
function updateTermItems() {
  termItems.value = [];
  let current = currentTermData.value.mapping;

  // 添加已有选项
  for (let i = 0; i < selectedOptions.value.length; i++) {
    const option = selectedOptions.value[i];
    termItems.value.push({
      options: Object.keys(current),
      selected: option
    });

    current = current[option];
  }

  // 检查当前层级
  if (typeof current === 'number') {
    currentScore.value = current;
    currentLevelIsObject.value = false;
  } else if (typeof current === 'object' && current !== null) {
    currentLevelIsObject.value = true;
    currentScore.value = null;

    // 添加下一个选择器
    termItems.value.push({
      options: Object.keys(current),
      selected: ''
    });
  } else {
    currentScore.value = null;
    currentLevelIsObject.value = false;
  }
}
// #endregion

// #region 导航-手动
const manualName = ref('');
const manualScoreInput = ref('');
const manualScore = ref(0);
const errorHint = ref('');

// #endregion

// #region 导航-成绩
const scores = computed(() => scoreModel.value.getAllScores());
const totalScore = computed(() => scoreModel.value.calculateTotalScore());

// #endregion

// 方法
function savequit() {
  if (!DataModel.currentLoginUser) {
    // 游客保存
    DataModel.visitor.scores = JSON.parse(JSON.stringify(scoreModel.value.getAllScores()));
  } else {
    // 已登录用户保存
    if (!DataModel.user.client) { DataModel.user.client = {} }
    DataModel.user.client.scores = scoreModel.value.getAllScores();
    DataModel.mergeCurrent()
    // 新用户加载时可能没有分数，就加载了游客的，继承游客分数后需要清空游客
    DataModel.visitor.scores = {};
    DataModel.saveAllToLocal()
  }
  // 关闭模态框
  closeModal();
}

function closeModal() {
  showMyscore.value = false;
}

function addScore() {
  if (!termNameInput.value) {
    errorHint.value = '请输入项目名称';
    return;
  }

  scoreModel.value.addScoreItem(termNameInput.value, currentScore.value, true);
  termNameInput.value = '';
  resetTermSelection();
  errorHint.value = '';
}

function addManualScore() {
  if (!termNameInput.value) {
    errorHint.value = '请输入项目名称';
    return;
  }

  if (isNaN(manualScore.value)) {
    errorHint.value = '请输入有效的分数';
    return;
  }

  scoreModel.value.addScoreItem(termNameInput.value, parseFloat(manualScore.value), false);
  termNameInput.value = '';
  manualScore.value = 0;
  resetTermSelection();
  errorHint.value = '';
}

function addManualItem() {
  if (!manualName.value) {
    errorHint.value = '请输入项目名称';
    return;
  }

  const score = parseFloat(manualScoreInput.value);
  if (isNaN(score)) {
    errorHint.value = '请输入有效的分数';
    return;
  }

  scoreModel.value.addScoreItem(manualName.value, score, false);
  manualName.value = '';
  manualScoreInput.value = '';
  errorHint.value = '';
}

function removeScore(index) {
  scoreModel.value.removeScoreItem(index);
}
// #endregion

// 初始化
onMounted(() => {
  // 初始化显示的活动
  circleRadius.value = window.innerWidth * 0.5 * 0.9
  nextTick(() => {
    if (DataModel.serverUpdating) {
      eventsLoading.value = true;
      console.log('服务器数据正在更新');
      (async () => {
        await DataModel.serverUpdatePromise;
        console.log('服务器数据更新完成');
        loadEvent();
      })();
    } else {
      loadEvent();
    }
    resetTermSelection();
  });
});



</script>

<style scoped>
.bonus-view-container {
  min-height: calc(100vh - 64px);
  max-height: calc(100vh - 64px);
  width: 100%;
  margin: 0;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

/* #region 导航 */
.nav-circle-container {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 90vw;
  max-width: 400px;
  height: 90vw;
  max-height: 400px;
  z-index: 5;
  pointer-events: none;
  /* background-color: #ff05; */
}

.nav-circle {
  width: 100%;
  height: 100%;
  border: 10px solid #000;
  border-radius: 50%;
  transform-origin: left center;
  transform: translate(50%, 30%);
  background-image: radial-gradient(circle at center, #4f1fffa0, #1f32ff40);
  pointer-events: auto;
  z-index: 25;
}

/* #region 导航点 */
.nav-point {
  position: absolute;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  background-size: cover;
  background-position: center;
  border: 2px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
  cursor: pointer;
  background-color: #777;
}

.nav-point:hover {
  transform: translate(-50%, -50%) scale(1.1);
  box-shadow: 0 0 20px #ff7e5fb3;
}

.nav-point.active {
  width: 64px;
  height: 64px;
  border: 3px solid #ff7e5f;
  box-shadow: 0 0 25px rgba(255, 126, 95, 0.8);
  z-index: 10;
}

.nav-label {
  position: absolute;
  top: 50%;
  right: 60px;
  transform: translateY(-50%);
  background: rgba(0, 0, 0, 0.7);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.3s ease;
  white-space: nowrap;
  pointer-events: none;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  background-color: #fffc;
}

.nav-circle-dragging .nav-point .nav-label {
  opacity: 1;
}

/* #endregion */

/* #region 导航心 */
.button-myscore {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-150%, -150%);
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #ffb012;

  display: flex;
  justify-content: center;
  align-items: center;
}

.button-myscore img {
  width: 58px;
  height: 58px;
}

/* #endregion */
/* #endregion */

/* #region 加分项目模态 */

.msmod-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.msmod-modal {
  width: 90%;
  min-height: 70vh;
  max-height: 70vh;
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* #region 头尾和小导航 */
.msmod-header {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
}

.msmod-header h3 {
  margin: 0;
  font-size: 1.4rem;
  color: #333;
}

.msmod-footer-btn-container {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
}

.msmod-footer {
  border-top: 2px solid #ff7e5f;
}

.msmod-footer-hint-container {
  font-size: 0.8rem;
  line-height: 1.1;
  color: red;
}

.msmod-footer-btn {
  width: 50%;
  height: 100%;
}

.msmod-title-container {
  width: 100%;
  display: flex;
  justify-content: space-around;
  flex-direction: row;
}

.msmod-navigator {
  width: 80%;
  display: flex;
  flex-direction: row;
  justify-content: space-around;
}

.msmod-navigator-btn {
  border: none;
  background: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #666;
}

.msmod-navigator-btn-active {
  color: #ff7e5f;
  font-weight: 600;
  border-bottom: 2px solid #ff7e5f;
}


/* #endregion */

/* #region 中间内容 */
.msmod-body-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
}


.msmod-body {
  flex-grow: 1;
  overflow-y: auto;
  padding: 12px 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.msmod-v-selections {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.msmod-h-selections {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.msmod-selection-interface-container {
  justify-content: space-around;
}

/* #region 项目头与介绍 */
.msmod-term-title-container {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.msmod-term-title {
  flex-grow: 1;
  font-size: 1.3rem;
  font-weight: 700;
  color: #42211a;
  text-align: center;
  min-width: 120px;
  padding-bottom: 4px;
  border-bottom: 2px solid #42211a;
}

.msmod-term-description {
  background-color: #fdf2df7f;
  padding: 12px;
  color: #653713;
  font-size: 0.9rem;
  border: 1px solid #e0e0e0;
}

.msmod-term-description span {
  font-weight: bold;
}

/* #endregion */



.msmod-form-label {
  margin-bottom: 5px;
  font-size: 0.95rem;
  color: #333;
}

.msmod-no-margin {
  margin: 0;
}

.msmod-form-input {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  background-color: white;
  font-size: 1rem;
  color: #424242;
  box-sizing: border-box;
}

.msmod-term-keys {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.msmod-term-mapping-item {
  width: 100%;
}


.msmod-term-mapping-item-content {
  display: flex;
  flex-direction: row;
  gap: 8px;
}

.msmod-form-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  background-color: white;
  font-size: 1rem;
  color: #424242;
  appearance: none;
  box-sizing: border-box;
}


.msmod-btn {
  background: none;
  border: 1px solid #bbb;
  cursor: pointer;
  text-align: center;
  font-size: 1rem;
  color: #666;
  padding: 8px 12px;
  box-sizing: border-box;
}

.msmod-btn-accept {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  background-color: white;
  font-size: 1rem;
  color: #424242;
  background-image: linear-gradient(73deg, #ffb836 17.88%, #ff6b4a 98.36%);
  color: #653713;
  cursor: pointer;
  text-align: center;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

th,
td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

th {
  background-color: #f5f5f5;
  font-weight: 600;
}

.msmod-delete-project {
  background-color: #ff6b4a;
  color: white;
  border: none;
  padding: 6px 12px;
  font-size: 0.9rem;
  cursor: pointer;
}

.msmod-error-hint {
  color: #ff6b4a;
  font-size: 0.9rem;
  margin-top: 5px;
  text-align: center;
}

#msmod-no-scores {
  text-align: center;
  color: #999;
}

/* #endregion */

/* #endregion */
</style>