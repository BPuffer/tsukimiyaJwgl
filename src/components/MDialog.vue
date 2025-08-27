<template>
  <div v-if="dialog._showing.value" class="dialog-mask">
    <div v-if="dialog.appearance.value === 'alert'" class="dialog-window">
      <div class="dialog-title">
        {{ title }}
      </div>
      <div class="dialog-message">
        <slot></slot>
      </div>
      <div class="dialog-buttons">
        <div class="dialog-button-yes" @click="dialog.alertConfirm">{{ confirmText }}</div>
      </div>
    </div>

    <div v-else-if="dialog.appearance.value === 'confirm'" class="dialog-window">
      <div class="dialog-title">
        {{ title }}
      </div>
      <div class="dialog-message">
        <slot></slot>
      </div>
      <div class="dialog-buttons">
        <div class="dialog-button-no" @click="dialog.confirmCancel">{{ cancelText }}</div>
        <div class="dialog-button-yes" @click="dialog.confirmConfirm">{{ confirmText }}</div>
      </div>
    </div>
    
    <div v-else-if="dialog.appearance.value === 'prompt'" class="dialog-window">
      <div class="dialog-title">
        {{ title }}
      </div>
      <div class="dialog-message">
        <slot></slot>
      </div>
      <div class="prompt-input">
        <input type="text" v-model="promptContent" placeholder="请输入">
      </div>
      <div class="dialog-buttons">
        <div class="dialog-button-no" @click="dialog.promptCancel">{{ cancelText }}</div>
        <div class="dialog-button-yes" @click="dialog.promptConfirm(promptContent)">{{ confirmText }}</div>
      </div>
    </div>

    <!-- load类型对话框(自定义的)：
     正常加载完成，使用dialog.loadComplete()方法的，返回true
     未正常加载完成，报错或手动取消的，返回false -->
    <div v-else-if="dialog.appearance.value === 'load'">
      <div class="dialog-window">
        <div class="dialog-title">
          {{ title }}
        </div>
        <div class="load-spinner-container"><div class="load-spinner"></div></div>
        <div class="dialog-message">
          <slot></slot>
        </div>
        <div class="dialog-buttons">
          <button class="dialog-button-no" :disabled="!loadCancelable" @click="dialog.loadCancel">{{ cancelText }}</button>
        </div>
      </div>
    </div>

    <div v-else class="dialog-window">
      <div class="dialog-title">
        错误：未指定对话框类型
      </div>
      <div class="dialog-message">
        这个问题大概率是由网站开发者造成的。您可以联系网站管理员获取帮助。
      </div>
      <div class="dialog-buttons">
        <div class="dialog-button-yes" @click="dialog.alertConfirm">{{ confirmText }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
const promptContent = ref('')
const props = defineProps({
  dialog: {
    type: Object,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: '确定'
  },
  cancelText: {
    type: String,
    default: '取消'
  },
  loadCancelable: {
    type: Boolean,
    default: true
  }
})
// 重置prompt输入框
watch(() => props.dialog.show.value, (newVal) => {
  if (newVal && props.dialog.appearance.value == 'prompt') promptContent.value = ''
})
</script>

<style scoped>
/* #region 根和公共 */
.dialog-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-window {
  width: 80vw;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: fadeIn 0.3s ease;
}

.dialog-title {
  padding: 20px 24px 12px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  text-align: center;
}

.dialog-message {
  padding: 0 24px 20px;
  font-size: 15px;
  line-height: 1.5;
  max-height: 50vh;
  overflow: auto;
  color: #666;
  text-align: center;
}

.dialog-buttons {
  display: flex;
  border-top: 1px solid #eee;
}

.dialog-button-yes, .dialog-button-no {
  flex: 1;
  padding: 14px 0;
  text-align: center;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.dialog-button-yes {
  color: #1890ff;
  font-weight: 600;
}

.dialog-button-yes:hover {
  background-color: #f0f9ff;
}

.dialog-button-yes:disabled {
  color: #999;
  text-decoration: line-through;
  cursor: not-allowed;
}

.dialog-button-no {
  color: #666;
  border-right: 1px solid #eee;
}

.dialog-button-no:hover {
  background-color: #f8f8f8;
}

.dialog-button-no:disabled {
  color: #999;
  text-decoration: line-through;
  cursor: not-allowed;
}

/* #endregion */

/* #region Prompt */
.prompt-input {
  padding: 0 24px 20px;
}

.prompt-input input {
  width: 100%;
  padding: 12px 16px;
  box-sizing: border-box;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  color: #333;
  background-color: #f9f9f9;
  transition: border-color 0.2s;
}

.prompt-input input:focus {
  border-color: #1890ff;
  outline: none;
  background-color: white;
}

.prompt-input input::placeholder {
  color: #999;
}
/* #endregion */

/* load */
.load-spinner-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.load-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #1890ff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>