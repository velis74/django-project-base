<script setup lang="ts">
import AppNotification from './components/notification.vue';
import LoginDialog from './components/user-session/login-dialog.vue';
</script>

<template>
  <BrowserCheck :hide-page-if-un-supported-browser="false">
    <v-app>
      <v-app-bar><TitleBar :breadcrumbs-component="null"/></v-app-bar>
      <v-main>
        <ModalView/>
        <LoginDialog/>
      </v-main>
      <app-notification/>
    </v-app>
  </BrowserCheck>
</template>
