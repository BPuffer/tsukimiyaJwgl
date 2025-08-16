<template>
  <div class="settings-container">
    <!-- 背景设置 -->
    <div class="setting-item">
      <div class="option-items">
        <div class="option" :class="{ disabled: bgType !== 'default-m1' }">
          <label>
            <div class="preview">
              <img src="/img/mbg1.jpg" alt="默认背景1">
            </div>
            <input type="radio" v-model="bgType" value="default-m1">
          </label>
        </div>

        <div class="option" :class="{ disabled: bgType !== 'default-m2' }">
          <label>
            <div class="preview">
              <img src="/img/mbg2.jpg" alt="默认背景2">
            </div>
            <input type="radio" v-model="bgType" value="default-m2">
          </label>
        </div>

        <div class="option" :class="{ disabled: bgType !== 'default-m3' }">
          <label>
            <div class="preview">
              <img src="/img/mbg3.jpg" alt="默认背景3">
            </div>
            <input type="radio" v-model="bgType" value="default-m3">
          </label>
        </div>

        <div class="option" :class="{ disabled: bgType !== 'default-m4' }">
          <label>
            <div class="preview">
              <img src="/img/mbg4.jpg" alt="默认背景4">
            </div>
            <input type="radio" v-model="bgType" value="default-m4">
          </label>
        </div>


        <div class="option" :class="{ disabled: bgType !== 'custom' }">
          <label>
            <div class="preview">
              <img v-if="bgImg" :ref="el => bgImgRef = el" :src="bgImg" alt="自定义背景">
              <div v-else @click="selectCustomImage" class="placeholder">
                <span>选择自定义背景</span>
              </div>
            </div>
            <input type="radio" v-model="bgType" value="custom" :disabled="!bgImg">
          </label>
          <input type="file" ref="bgFileInput" accept="image/*" style="display: none" @change="handleFileUpload">
        </div>
      </div>
    </div>

    <!-- 许可协议 -->
    <div class="setting-item">
      <div class="setting-item-actionbtn" @click="openLicense">
        许可协议
      </div>
      <MDialog :dialog="dialogLicense" title="许可协议" confirmText="同意" cancelText="不同意">
        <iframe 
          src="/license-vlast.html" 
          frameborder="0"
          style="width:100%; height:400px"
        ></iframe>
        <p>协议版本：<a :href="`/license-v${LICENSE_VERSION}.html`" target="_blank">v{{ LICENSE_VERSION }}</a></p>
      </MDialog>
    </div>
    
    <!-- 清空数据 -->
    <div class="setting-item">
      <div class="setting-item-actionbtn" @click="clearAllData">
        清空本地所有数据
      </div>
      <MDialog :dialog="dialogClearData" title="清空本地所有数据">
        <p>确定要清空本地所有数据吗？此操作不可撤销！</p>
      </MDialog>
    </div>
    
    <!-- 测试按钮 -->
    <!-- <div class="setting-item">
      <div class="setting-item-actionbtn" @click="testBtn">
        测试按钮
      </div>
      <MDialog :dialog="dialogTest" title="测试按钮" :loadCancelable="false">
        <p>测试按钮</p>
        <table>
          <tr><th>姓名</th><th>年龄</th></tr>
          <tr><td>张三</td><td>18</td></tr>
        </table>
        <div v-html="testhtml"></div>
        <u @click="dialogTest.loadComplete()">加载完成</u>
        <u @click="dialogTest.loadCancel()">加载取消</u>
      </MDialog>
    </div> -->
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import DataModel from '@/models/DataModel'
import Hammer from 'hammerjs'
import StyleManager from '@/models/styleManager.js';
import MDialog from '@/components/MDialog.vue'
import createDialog from '@/models/dialogs.js'
import { LICENSE_VERSION } from '../../models/version';

// #region 背景设置
const bgFileInput = ref(null)
const defaultBg = 'default-m3';
// 初始化背景类型
if (!DataModel.settings.bgImg) { DataModel.settings.bgImg = null }
if (!DataModel.settings.bgType) { DataModel.settings.bgType = defaultBg }
const bgType = ref(DataModel.settings.bgType)
const bgImg = ref(DataModel.settings.bgImg)
// 监听背景类型选项变化
watch(bgType, (newVal) => {
  DataModel.settings.bgType = bgType.value;
  DataModel.settings.bgImg = bgImg.value
  StyleManager.changeBg()
  DataModel.saveAllToLocal()
})
// 选择自定义图片
const selectCustomImage = () => {
  bgFileInput.value.click()
}
// 处理文件上传
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file || !file.type.match('image.*')) return
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      bgImg.value = e.target.result
      bgType.value = 'custom'
    } catch (err) {
      bgType.value = defaultBg
    }
  }
  reader.readAsDataURL(file)
  // 重置input以允许重复选择
  event.target.value = null
}
const bgImgRef = ref(null)
const bgImgHammer = ref(null)
const isLongPress = ref(false);
function initHammer() {
  bgImgHammer.value = new Hammer(bgImgRef.value);
  bgImgHammer.value.get('press').set({ time: 300 });
  bgImgHammer.value.on('press', () => {
    isLongPress.value = true;
    bgType.value = defaultBg;
    bgImg.value = null;
    DataModel.settings.bgImg = null;
  });
  bgImgHammer.value.on('pressup', () => {
    setTimeout(() => { isLongPress.value = false }, 100);
  });
}
watch(() => bgImgRef.value, (bgImgRef) => {
  if (bgImgRef.value) {
    initHammer()
  }
})
// #endregion 背景设置

// #region 清空数据
const dialogClearData = createDialog()
async function clearAllData() {
  if (await dialogClearData.confirm()) {
    await DataModel.clearLocal()
    // 导向根
    window.location.href = '/'
  }
}
// #endregion 清空数据

// #region 许可协议
const dialogLicense = createDialog()
async function openLicense() {
  const confirmLicenseWindow = dialogLicense.confirm()
  if (await confirmLicenseWindow) {
    DataModel.agreeLicense()
  } else {
    DataModel.clearLicense()
  }
}
// #endregion 许可协议

// #region 测试按钮
// const dialogTest = createDialog()
// async function testBtn() {
//   const result = await dialogTest.load()
//   console.log('测试按钮返回:', result)
// }
// const testhtml = ref('<u>看看是不是啥都能塞进去</u>')
// #endregion 测试按钮

onMounted(() => {
  nextTick(() => {
    if (bgImgRef.value) {
      initHammer()
    }
  })
})

onUnmounted(() => {
  if (bgImgHammer.value) {
    bgImgHammer.value.destroy();
    bgImgHammer.value = null;
  }
});

</script>

<style scoped>
/* #region 设置主框架 */
.settings-container {
  background-color: #fff7f7c0;
  padding: 16px;
  box-sizing: border-box;
}

.setting-item {
  width: 100%;
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid #888c;
}

.setting-item-actionbtn {
  width: 100%;
  box-sizing: border-box;
  padding: 16px;
  font-size: 14px;
  color: #212121;
  background: transparent;
  border: none;
  text-align: left;
  position: relative;
}

.setting-item-actionbtn::after {
  content: "\203A";
  font-size: 2em;

  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
}

.setting-item-actionbtn:active {
  background: rgba(0, 0, 0, 0.1);
}
/* #endregion */

/* #region 多项设置 */
.option-items {
  display: flex;
  flex-direction: row;
  gap: 10px;

}

.option {
  width: 100%;
  padding: 12px 0;
}

.option label {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.option input[type="radio"] {
  margin-right: 12px;
}

.preview {
  width: 100%;
  aspect-ratio: 9/16;
  background-color: #f0f0f0;
  overflow: hidden;
  border-radius: 8px;
  position: relative;
}

.preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #666;
  font-size: 14px;
  background: repeating-linear-gradient(45deg,
      #f5f5f5,
      #f5f5f5 10px,
      #e0e0e0 10px,
      #e0e0e0 20px);
}
/* #endregion */

.disabled {
  opacity: 0.6;
}

.disabled .preview {
  cursor: not-allowed;
}

</style>