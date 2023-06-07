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
import { apiClient, APIConsumer, ConsumerLogicApi } from '@velis/dynamicforms';
import { defineComponent, ref } from 'vue';

import { PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME } from './user-session/data-types';

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
    this.consumerLogic.filterData = { 'remove-merge-users': true };
    (async () => {
      await this.consumerLogic.getFullDefinition();
    })();
    (async () => {
      await this.consumerLogicMerge.getFullDefinition();
    })();
    // this.mergeRefreshInterval = setInterval(() => {
    //   this.consumerLogicMerge.reload();
    // }, 1000);
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
    actionMergeUsers(payload) {
      console.log(Math.random(), payload, 'merge users');
      apiClient.post('account/profile-merge').then(() => {
        this.consumerLogicMerge.reload();
      });
    },
    actionClearMergeUsers(payload) {
      console.log(Math.random(), payload, 'clear merge users');
      apiClient.delete('account/profile-merge/clear').then(() => {
        this.consumerLogicMerge.reload();
        this.consumerLogic.reload();
      });
    },
    actionAddToMerge(action, payload) {
      console.log(Math.random(), action, payload, 'add to merge users');
      apiClient.post('account/profile/merge', { user: payload[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME] }).then(() => {
        this.consumerLogicMerge.reload();
        // noinspection ES6ShorthandObjectProperty
        this.consumerLogic.reload();
      });
    },
  },
});
</script>
