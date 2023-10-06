<script setup lang="ts">
import { Action, dfModal, DialogSize, FilteredActions, gettext } from '@velis/dynamicforms';
import { storeToRefs } from 'pinia';
import { h, watch } from 'vue';

import ProfileSearch from './profile-search.vue';

const { selectedProjectId } = storeToRefs(userSession);

if (selectedProjectId.value) refreshSettingsLogic();

watch(selectedProjectId, refreshSettingsLogic);

function selected(val) {
  console.log('EEEERRRRR', val);
}

async function showAddProfileModal() {
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
  <button @click="showAddProfileModal">sdfsdf</button>
  </div>
</template>
