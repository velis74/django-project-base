<template>
  <div v-if="!pageHidden">
    <slot/>
  </div>
</template>

<script lang="ts">
import browserUpdate from 'browser-update';
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'BrowserCheck',
  props: {
    hidePageIfUnSupportedBrowser: {
      type: Boolean,
      default: false,
    },
    numberOfLastBrowserVersionsSupported: {
      type: Number,
      default: 4,
    },
  },
  data() {
    return {
      pageHidden: false,
      checkInterval: null as any,
    };
  },
  beforeDestroy() {
    this.clearCheck();
    this.pageHidden = false;
  },
  mounted() {
    browserUpdate({
      required: {
        e: -this.numberOfLastBrowserVersionsSupported,
        f: -this.numberOfLastBrowserVersionsSupported,
        o: -this.numberOfLastBrowserVersionsSupported,
        s: -this.numberOfLastBrowserVersionsSupported,
        c: -this.numberOfLastBrowserVersionsSupported,
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
});
</script>
