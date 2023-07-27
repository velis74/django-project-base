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

<script setup lang="ts">
import { Action, apiClient, APIConsumer, ComponentDisplay, ConsumerLogicApi } from '@velis/dynamicforms';

import { PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME } from './data-types';

const consumerLogic = new ConsumerLogicApi('/account/profile', false);
const consumerLogicMerge = new ConsumerLogicApi('/account/profile-merge', false);
const displayComponent = ComponentDisplay.TABLE;

consumerLogic.filterData = { 'remove-merge-users': true };

consumerLogic.getFullDefinition();
consumerLogicMerge.getFullDefinition();

const actionMergeUsers = () => {
  apiClient.post('account/profile-merge').then(() => {
    consumerLogicMerge.reload();
  });
};

const actionClearMergeUsers = () => {
  apiClient.delete('account/profile-merge/clear').then(() => {
    consumerLogicMerge.reload();
    consumerLogic.reload();
  });
};

const actionAddToMerge = (action: Action, payload: { [x: string]: any; }) => {
  apiClient.post('account/profile/merge', { user: payload[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME] }).then(() => {
    consumerLogicMerge.reload();
    consumerLogic.reload();
  });
};

defineExpose({
  actionMergeUsers,
  actionClearMergeUsers,
  actionAddToMerge,
});
</script>

<style scoped>
.full-width {
  display: flex;
}

.full-width > * { flex: 1; }
</style>
