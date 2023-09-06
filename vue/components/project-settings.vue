<script setup lang="ts">
import { APIConsumer, ComponentDisplay, ConsumerLogicApi } from '@velis/dynamicforms';
import { storeToRefs } from 'pinia';
import { ref, watch } from 'vue';

import { useUserSessionStore } from '../apps';

const userSession = useUserSessionStore();
const settingsLogic = ref(new ConsumerLogicApi('/project-settings', false));

const { selectedProjectId } = storeToRefs(userSession);

function refreshSettingsLogic() {
  settingsLogic.value.getFullDefinition();
  settingsLogic.value.reload();
}

if (selectedProjectId.value) refreshSettingsLogic();

watch(selectedProjectId, refreshSettingsLogic);

</script>

<template>
  <div class="overflow-y-auto">
    <APIConsumer
      :consumer="settingsLogic"
      :display-component="ComponentDisplay.TABLE"
    />
  </div>
</template>
