<template>
  <div v-if="!pageHidden">
    <slot/>
  </div>
</template>

<script>
import browserUpdate from 'browser-update';

export default {
  name: 'BrowserCheck',
  props: {
    hidePageIfUnSupportedBrowser: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      pageHidden: false,
      checkInterval: null,
    };
  },
  beforeDestroy() {
    this.clearCheck();
    this.pageHidden = false;
  },
  mounted() {
    browserUpdate({
      required: {
        e: -4, f: -4, o: -4, s: -4, c: -4,
      },
      insecure: true,
      unsupported: true,
      reminder: 0,
      reminderClosed: 1,
      noclose: true,
    }, false);
    this.checkInterval = setInterval(() => {
      if (this.hidePageIfUnSupportedBrowser && this.isBrowserNotificationShown() && !this.pageHidden) {
        this.pageHidden = true;
      }
    }, 250);
    setTimeout(() => {
      this.clearCheck();
    }, 10000);
  },
  methods: {
    isBrowserNotificationShown() {
      return !!document.getElementById('buorg');
    },
    clearCheck() {
      if (this.checkInterval) {
        clearInterval(this.checkInterval);
        this.checkInterval = null;
      }
    },
  },
};
</script>
