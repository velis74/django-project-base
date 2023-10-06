<script setup lang="ts">
import { Action, ConsumerLogicApi, dfModal, DialogSize, FilteredActions, gettext } from '@velis/dynamicforms';
import { storeToRefs } from 'pinia';
import { h, ref, watch } from 'vue';

import { apiClient } from '../apiClient';

import ProfileSearch from './profile-search.vue';
import useUserSessionStore from './user-session/state';

const userSession = useUserSessionStore();
const settingsLogic = ref(new ConsumerLogicApi('/project-settings', false));

const { selectedProjectId } = storeToRefs(userSession);

function refreshSettingsLogic() {
  settingsLogic.value.getFullDefinition();
  settingsLogic.value.reload();
}

if (selectedProjectId.value) refreshSettingsLogic();

watch(selectedProjectId, refreshSettingsLogic);

function selected(val) {
  console.log('EEEERRRRR', val);
}

async function showModal() {
  const modal = await dfModal.message('TTIEL', () => [h('div', [h(ProfileSearch, { onSelected: selected })])], new FilteredActions({
    cancel: new Action({
      name: 'cancel',
      label: gettext('Cancel'),
      displayStyle: { asButton: true, showLabel: true, showIcon: true },
      position: 'FORM_FOOTER',
    }),
    confirm: new Action({
      name: 'add',
      label: gettext('Add'),
      displayStyle: { asButton: true, showLabel: true, showIcon: true },
      position: 'FORM_FOOTER',
    }),
  }), { size: DialogSize.LARGE });

  if (modal.action.name === 'add') {
    console.log('ADDDD ');
  }
}

</script>

<template>
  <div>
    <profile-search/>

    <br/>
    <br/>

    <button @click="showModal">sdfsdf</button>
  </div>
</template>
