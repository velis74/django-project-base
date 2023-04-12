<template>
  <BrowserCheck :hide-page-if-un-supported-browser="false">
    <v-app>
      <v-app-bar><TitleBar :breadcrumbs-component="null"/></v-app-bar>
      <v-main>
        <ModalView/>
      </v-main>
    </v-app>
  </BrowserCheck>
</template>
<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({ name: 'TitlebarAppStandalone' });
</script>
