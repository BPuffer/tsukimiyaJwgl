// dialogs.js
import { ref } from 'vue'

export default function createDialog() {
  const show = ref(false)
  const title = ref('')
  const appearance = ref('')
  let resolvePromise = null

  // #region alert
  function alert() {
    show.value = true
    appearance.value = 'alert'
    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  function alertConfirm() {
    show.value = false
    if (resolvePromise) {
      resolvePromise(true)
      resolvePromise = null
    }
  }
  // #endregion

  // #region confirm
  function confirm() {
    show.value = true
    appearance.value = 'confirm'
    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  function confirmCancel() {
    show.value = false
    if (resolvePromise) {
      resolvePromise(false)
      resolvePromise = null
    }
  }

  function confirmConfirm() {
    show.value = false
    if (resolvePromise) {
      resolvePromise(true)
      resolvePromise = null
    }
  }
  // #endregion

  // #region prompt
  function prompt() {
    show.value = true
    appearance.value = 'prompt'
    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  function promptConfirm(content) {
    show.value = false
    if (resolvePromise) {
      resolvePromise(content)
      resolvePromise = null
    }
  }

  function promptCancel() {
    show.value = false
    if (resolvePromise) {
      resolvePromise(null)
      resolvePromise = null
    }
  }
  // #endregion

  // #region load
  function load() {
    show.value = true
    appearance.value = 'load'
    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  function loadComplete() {
    show.value = false
    if (resolvePromise) {
      resolvePromise(true)
      resolvePromise = null
    }
  }

  function loadCancel() {
    show.value = false
    if (resolvePromise) {
      resolvePromise(false)
      resolvePromise = null
    }
  }
  // #endregion

  return {
    show,
    title,
    appearance,
    alert,
    alertConfirm,
    confirm,
    confirmConfirm,
    confirmCancel,
    prompt,
    promptConfirm,
    promptCancel,
    load,
    loadComplete,
    loadCancel,
  }
}