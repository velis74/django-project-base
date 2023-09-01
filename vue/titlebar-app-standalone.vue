<script setup lang="ts">
import AppNotification from './components/notification.vue';
import NotificationsEditor from './components/notifications-editor.vue';
import LoginDialog from './components/user-session/login-dialog.vue';
</script>

<template>
  <BrowserCheck :hide-page-if-un-supported-browser="false">
    <v-app>
      <v-app-bar><TitleBar :breadcrumbs-component="null"/></v-app-bar>
      <v-main>
        <notifications-editor/>
        <ModalView/>
        <LoginDialog/>
      </v-main>
    </v-app>
  </BrowserCheck>
  <app-notification/>
</template>
