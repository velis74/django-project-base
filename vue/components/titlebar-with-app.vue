<template>
  <v-app>
    <v-app-bar>
      <slot name="titlebar"/>
    </v-app-bar>
    <slot v-if="sessionStore.loggedIn && sessionStore.anyProjectSelected" name="application"/>
    <!--    <div v-else-if="sessionStore.loggedIn">-->
    <!--      <v-container>-->
    <!--        <APIConsumer :consumer="projectConsumer" :display-component="ComponentDisplay.TABLE"/>-->
    <!--      </v-container>-->
    <!--    </div>-->
    <slot v-else name="landing-page"/>
    <ModalView/>
  </v-app>
</template>

<script setup lang="ts">

import { APIConsumer, ComponentDisplay, ConsumerLogicApi } from '@velis/dynamicforms';
import { ref } from 'vue';

import useUserSessionStore from './user-session/state';

const sessionStore = useUserSessionStore();

const projectConsumer = ref(new ConsumerLogicApi('/project', false));
(async () => {
  await projectConsumer.value.getFullDefinition();
})();

</script>
