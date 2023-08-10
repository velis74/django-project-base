<script setup lang="ts">
import { APIConsumer, ComponentDisplay, ConsumerLogicApi } from '@velis/dynamicforms';
import { ref } from 'vue';

const notificationLogic = ref(new ConsumerLogicApi('notification', true));

(async () => {
  await notificationLogic.value.getFullDefinition();
})();
// TODO: remove linter ignores below when you know how to
</script>

<template>
  <div class="overflow-y-auto">
    <!--suppress TypeScriptValidateTypes -->
    <!-- @vue-ignore -->
    <APIConsumer :consumer="notificationLogic" :display-component="ComponentDisplay.TABLE"/>
    <ModalView/>
  </div>
</template>
