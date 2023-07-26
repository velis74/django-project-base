<script setup lang="ts">
import LoginDialog from './components/user-session/login-dialog.vue';
</script>

<template>
  <BrowserCheck :hide-page-if-un-supported-browser="false">
    <v-app>
      <v-app-bar><TitleBar :breadcrumbs-component="undefined"/></v-app-bar>
      <v-main>
        <ModalView/>
        <LoginDialog/>
      </v-main>
    </v-app>
  </BrowserCheck>
</template>
