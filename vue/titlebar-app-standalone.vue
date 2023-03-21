<template>
  <v-app>
    <v-main>
      <BrowserCheck :hide-page-if-un-supported-browser="false">
        <TitleBar :breadcrumbs-component="null"/>
        <ModalView/>
      </BrowserCheck>
    </v-main>
  </v-app>
</template>
<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({ name: 'TitlebarAppStandalone' });
</script>
