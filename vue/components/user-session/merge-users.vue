<template>
  <div>
    <div class="full-width">
      <div>
        <APIConsumer :consumer="consumerLogic" :display-component="displayComponent"/>
      </div>
      <div>
        <APIConsumer :consumer="consumerLogicMerge" :display-component="displayComponent"/>
      </div>
    </div>
    <ModalView/>
  </div>
</template>

<script lang="ts">
import { Action, apiClient, APIConsumer, ComponentDisplay, ConsumerLogicApi } from '@velis/dynamicforms';
import { defineComponent, ref } from 'vue';

import { PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME } from './data-types';

export default defineComponent({
  name: 'MergeUsers',
  components: { APIConsumer },
  data() {
    return {
      consumerLogic: ref<ConsumerLogicApi>(new ConsumerLogicApi('/account/profile', false)),
      consumerLogicMerge: ref<ConsumerLogicApi>(new ConsumerLogicApi('/account/profile-merge', false)),
      displayComponent: ComponentDisplay.TABLE,
    };
  },
  mounted() {
    // @ts-ignore
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
    actionAddToMerge(action: Action, payload: { [x: string]: any; }) {
      apiClient.post('account/profile/merge', { user: payload[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME] }).then(() => {
        this.consumerLogicMerge.reload();
        this.consumerLogic.reload();
      });
    },
  },
});
</script>

<style scoped>
.full-width {
  display: flex;
}

.full-width > * { flex: 1; }
</style>
