<template>
  <div style="display: flex; flex-direction: row;">
    <div style="width: 45%; margin-right: 3%;">
      <APIConsumer :consumer="consumerLogic" :display-component="1"/>
    </div>
    <div style="width: 45%;">
      <APIConsumer :consumer="consumerLogicMerge" :display-component="1"/>
    </div>
    <ModalView/>
  </div>
</template>

<script lang="ts">
import { APIConsumer, ConsumerLogicApi } from '@velis/dynamicforms';
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
      consumerLogicMerge: ref<ConsumerLogicApi>(new ConsumerLogicApi('/account/profile-merge', false)),
      mergeRefreshInterval: null as any,
    };
  },
  beforeDestroy() {
    this.clearCheck();
    this.pageHidden = false;
    if (this.mergeRefreshInterval) {
      clearInterval(this.mergeRefreshInterval);
      this.mergeRefreshInterval = null;
    }
  },
  mounted() {
    console.log(Math.random());
    (async () => {
      await this.consumerLogic.getFullDefinition();
    })();
    (async () => {
      await this.consumerLogicMerge.getFullDefinition();
    })();
    this.mergeRefreshInterval = setInterval(() => {
      this.consumerLogicMerge.reload();
    }, 1000);
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
    actionAddToGroup(t) {
      console.log(Math.random(), t, 'fghfg');
    },
  },
});
</script>
