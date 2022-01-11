<template>
  <div style="display: none"/>
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
      a: null,
    };
  },
  mounted() {
    console.log(this.lockScreen);
    browserUpdate({
      required: {
        e: -3, f: -3, o: -3, s: -3, c: -3,
      },
      insecure: true,
      unsupported: true,
      reminder: 0,
      reminderClosed: 1,
      noclose: true,
      // test: true,
    });
    this.checkInterval = setInterval(() => {
      console.log(this.isBrowserNotificationShown() && this.lockScreen);
      if (this.isBrowserNotificationShown() && this.lockScreen) {
        // eslint-disable-next-line no-debugger
        debugger;
        console.log('notification shown');
      }
    }, 250);
  },
  methods: {
    isBrowserNotificationShown() {
      console.log('check', Math.random());
      return document.cookie.indexOf('browserupdateorg=pause') > -1;
    },
  },
};
</script>

<style scoped>

</style>
