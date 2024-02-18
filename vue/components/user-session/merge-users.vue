<template>
  <div>
    <div class="full-width">
      <div>
        <!--suppress TypeScriptValidateTypes -->
        <!-- @vue-ignore -->
        <APIConsumer :consumer="consumerLogic" :display-component="displayComponent"/>
      </div>
      <div>
        <!--suppress TypeScriptValidateTypes -->
        <!-- @vue-ignore -->
        <APIConsumer :consumer="consumerLogicMerge" :display-component="displayComponent"/>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// TODO: remove linter ignores above when you know how to
import {
  Action,
  apiClient,
  APIConsumer,
  ComponentDisplay,
  ConsumerLogicApi,
  useActionHandler,
} from '@velis/dynamicforms';

import { PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME } from './data-types';

const consumerLogic = new ConsumerLogicApi('/account/profile', false);
const consumerLogicMerge = new ConsumerLogicApi('/account/profile-merge', false);
const displayComponent = ComponentDisplay.TABLE;

consumerLogic.filterData = { 'remove-merge-users': true };

consumerLogic.getFullDefinition();
consumerLogicMerge.getFullDefinition();

const actionMergeUsers = async () => {
  await apiClient.post('account/profile-merge').then(() => {
    consumerLogicMerge.reload();
  });
  return true;
};

const actionClearMergeUsers = async () => {
  await apiClient.delete('account/profile-merge/clear').then(() => {
    consumerLogicMerge.reload();
    consumerLogic.reload();
  });
  return true;
};

const actionAddToMerge = async (action: Action, payload: { [x: string]: any; }) => {
  await apiClient.post('account/profile/merge', { user: payload[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME] }).then(() => {
    consumerLogicMerge.reload();
    consumerLogic.reload();
  });
  return true;
};

const { handler } = useActionHandler();

handler.register('merge-users', actionMergeUsers)
  .register('clear-merge-users', actionClearMergeUsers)
  .register('add-to-merge', actionAddToMerge);
</script>

<style scoped>
.full-width {
  display: flex;
}

.full-width > * { flex: 1; }
</style>
