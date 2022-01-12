<template>
  <div v-if="lockOverlayVisible" class="lockScreen" @touchmove.self.prevent>
  </div>
</template>

<script>
import browserUpdate from 'browser-update';

export default {
  name: 'BrowserCheck',
  props: {
    lockScreen: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      pageLocked: false,
      checkInterval: null,
      lockOverlayVisible: false,
    };
  },
  beforeDestroy() {
    clearInterval(this.checkInterval);
    this.checkInterval = null;
    document.body.style.overflow = '';
    this.lockOverlayVisible = false;
    this.pageLocked = false;
  },
  mounted() {
    browserUpdate({
      required: {
        e: -3, f: -3, o: -3, s: -3, c: -3,
      },
      insecure: true,
      unsupported: true,
      reminder: 0,
      reminderClosed: 1,
      noclose: true,
    }, false);
    this.checkInterval = setInterval(() => {
      if (this.lockScreen && this.isBrowserNotificationShown() && !this.pageLocked) {
        this.lockFullScreen();
      }
    }, 250);
  },
  methods: {
    isBrowserNotificationShown() {
      return !!document.getElementById('buorg');
    },
    lockFullScreen() {
      this.pageLocked = true;
      this.lockOverlayVisible = true;
      document.body.style.overflow = 'hidden';
    },
  },
};
</script>

<style scoped>
  .lockScreen {
    position: fixed;
    width: 100%;
    height: 100%;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: rgba(0, 0, 0, .5);
    z-index: 100000;
  }
</style>
