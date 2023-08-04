<script setup lang="ts">
import { APIConsumer, ComponentDisplay, ConsumerLogicApi } from '@velis/dynamicforms';
import { ref } from 'vue';

const notificationLogic = ref(new ConsumerLogicApi('notification', true));

(async () => {
  await notificationLogic.value.getFullDefinition();
})();

</script>

<template>
  <div class="overflow-y-auto">
    <APIConsumer
      :consumer="notificationLogic"
      :display-component="ComponentDisplay.TABLE"
    />
    <ModalView/>
  </div>
</template>
