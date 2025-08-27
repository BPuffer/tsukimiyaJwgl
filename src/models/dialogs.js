// dialogs.js
import { ref } from 'vue'

export default function createDialog(type_='alert') {
  const _showing = ref(false)
  const appearance = ref('')
  const type = ref(type_)
  let resolvePromise = null

  // #region alert
  function alert() {
    _showing.value = true
    appearance.value = 'alert'
    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  function alertConfirm() {
    _showing.value = false
    if (resolvePromise) {
      resolvePromise(true)
      resolvePromise = null
    }
  }
  // #endregion

  // #region confirm
  function confirm() {
    _showing.value = true
    appearance.value = 'confirm'
    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  function confirmCancel() {
    _showing.value = false
    if (resolvePromise) {
      resolvePromise(false)
      resolvePromise = null
    }
  }

  function confirmConfirm() {
    _showing.value = false
    if (resolvePromise) {
      resolvePromise(true)
      resolvePromise = null
    }
  }
  // #endregion

  // #region prompt
  function prompt() {
    _showing.value = true
    appearance.value = 'prompt'
    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  function promptConfirm(content) {
    _showing.value = false
    if (resolvePromise) {
      resolvePromise(content)
      resolvePromise = null
    }
  }

  function promptCancel() {
    _showing.value = false
    if (resolvePromise) {
      resolvePromise(null)
      resolvePromise = null
    }
  }
  // #endregion

  // #region load
  function load() {
    _showing.value = true
    appearance.value = 'load'
    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  function loadComplete() {
    _showing.value = false
    if (resolvePromise) {
      resolvePromise(true)
      resolvePromise = null
    }
  }

  function loadCancel() {
    _showing.value = false
    if (resolvePromise) {
      resolvePromise(false)
      resolvePromise = null
    }
  }
  // #endregion

  function show() {
    if (type == 'alert') {
      alert()
    } else if (type == 'confirm') {
      confirm()
    } else if (type == 'prompt') {
      prompt()
    } else if (type == 'load') {
      load()
    }
  }

  return {
    _showing,
    appearance,
    type,
    show,
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