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

import { PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME } from './data-types';

export default defineComponent({
  name: 'MergeUsersExample',
  components: { APIConsumer },
  data() {
    return {
      consumerLogic: ref<ConsumerLogicApi>(new ConsumerLogicApi('/account/profile', false)),
      consumerLogicMerge: ref<ConsumerLogicApi>(new ConsumerLogicApi('/account/profile-merge', false)),
    };
  },
  mounted() {
    this.consumerLogic.filterData = { 'remove-merge-users': true };
    (async () => {
      await this.consumerLogic.getFullDefinition();
    })();
    (async () => {
      await this.consumerLogicMerge.getFullDefinition();
    })();
  },
  methods: {
    actionMergeUsers() {
      apiClient.post('account/profile-merge').then(() => {
        this.consumerLogicMerge.reload();
      });
    },
    actionClearMergeUsers() {
      apiClient.delete('account/profile-merge/clear').then(() => {
        this.consumerLogicMerge.reload();
        this.consumerLogic.reload();
      });
    },
    actionAddToMerge(action, payload) {
      apiClient.post('account/profile/merge', { user: payload[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME] }).then(() => {
        this.consumerLogicMerge.reload();
        // noinspection ES6ShorthandObjectProperty
        this.consumerLogic.reload();
      });
    },
  },
});
</script>
