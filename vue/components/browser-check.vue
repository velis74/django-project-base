<template>
  <div>
    <APIConsumer :consumer="consumerLogic" :display-component="1"/>
  </div>
</template>

<script lang="ts">
import { APIConsumer, ConsumerLogicApi } from '@velis/dynamicforms';
// import browserUpdate from 'browser-update';
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'BrowserCheck',
  components: { APIConsumer },
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
      consumerLogic: ref<ConsumerLogicApi>(new ConsumerLogicApi('/account/profile', false)),
    };
  },
  beforeDestroy() {
    this.clearCheck();
    this.pageHidden = false;
  },
  mounted() {
    console.log(Math.random());
    (async () => {
      await this.consumerLogic.getFullDefinition();
    })();
    // browserUpdate({
    //   required: {
    //     e: -this.numberOfLastBrowserVersionsSupported,
    //     f: -this.numberOfLastBrowserVersionsSupported,
    //     o: -this.numberOfLastBrowserVersionsSupported,
    //     s: -this.numberOfLastBrowserVersionsSupported,
    //     c: -this.numberOfLastBrowserVersionsSupported,
    //   },
    //   insecure: true,
    //   unsupported: true,
    //   reminder: 0,
    //   reminderClosed: 1,
    //   noclose: true,
    // }, false);
    // this.checkInterval = setInterval(() => {
    //   if (this.hidePageIfUnSupportedBrowser && this.isBrowserNotificationShown() && !this.pageHidden) {
    //     this.pageHidden = true;
    //   }
    // }, 250);
    // setTimeout(() => {
    //   this.clearCheck();
    // }, 10000);
  },
  methods: {
    isBrowserNotificationShown() {
      return !!document.getElementById('buorg');
    },
    clearCheck() {
      // if (this.checkInterval) {
      //   clearInterval(this.checkInterval);
      //   this.checkInterval = null;
      // }
    },
  },
});
</script>
