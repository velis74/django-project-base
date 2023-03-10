<template>
  <v-app>
    <v-main>
      <BrowserCheck :hidePageIfUnSupportedBrowser="false">
        <TitleBar v-slot:content :projectlistVisible="true"/>
      </BrowserCheck>
    </v-main>
  </v-app>
</template>
<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({ name: 'TitlebarAppStandalone' });
</script>
