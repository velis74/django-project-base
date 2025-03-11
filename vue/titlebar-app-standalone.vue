<script setup lang="ts">
import DpbApp from './dpb-app.vue';
</script>

<template>
  <browser-check :hide-page-if-un-supported-browser="false">
    <v-app>
      <v-app-bar><title-bar :breadcrumbs-component="null"/></v-app-bar>
      <v-main>
        <dpb-app/>
      </v-main>
    </v-app>
  </browser-check>
</template>
