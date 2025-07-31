<template>
  <v-toolbar :theme="darkOrLightMode">
    <template v-if="userSession.selectedProject?.logo" #prepend>
      <v-img :src="userSession.selectedProject.logo" @click="clickLogo"/>
    </template>
    <v-toolbar-title @click="(event) => emit('title-click', event)">{{ computeTitle() }}</v-toolbar-title>
    <template v-if="breadcrumbsComponent && userSession.loggedIn" #extension>
      <breadcrumbs v-if="breadcrumbsComponent === 'Breadcrumbs'"/>
      <component :is="breadcrumbsComponent" v-else/>
    </template>
    <div class="flex-grow-0"/>
    <template v-if="props.projectListComponent && userSession.loggedIn && !display.smAndDown.value">
      <project-list v-if="projectListComponent === 'ProjectList'"/>
      <component :is="projectListComponent" v-else/>
    </template>
    <template v-if="userProfileComponent && userSession.loggedIn">
      <user-profile v-if="userProfileComponent === 'UserProfile'" :project-list-component="projectListComponent"/>
      <component :is="userProfileComponent" v-else :project-list-component="projectListComponent"/>
    </template>
    <LoginInline v-else-if="!userSession.loggedIn && loginVisible"/>
  </v-toolbar>
</template>

<script setup lang="ts">
import { apiClient } from '@velis/dynamicforms';
import _ from 'lodash-es';
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useDisplay } from 'vuetify';

import { API_CONFIG } from '../api-config';
import { maintenanceNotificationAcknowledged as MaintenanceNotificationAcknowledged } from '../events';
import { showMaintenanceNotification } from '../notifications';

import Breadcrumbs from './breadcrumbs.vue';
import LoginInline from './user-session/login-inline.vue';
import ProjectList from './user-session/project-list.vue';
import useUserSessionStore from './user-session/state';
import UserProfile from './user-session/user-profile.vue';

const props = defineProps({
  darkMode: { type: Boolean, default: false }, // dark mode on when true
  title: { type: String, default: null }, // set to override automatic title composition
  pageTitle: { type: String, default: null }, // set to add page title to currently selected project name
  adjustDocumentTitle: { type: Boolean, default: true }, // when true, will adjust document title based on page title
  projectListComponent: { type: String, default: 'ProjectList' }, // specify your own globally registered component
  userProfileComponent: { type: String, default: 'UserProfile' }, // specify your own globally registered component
  breadcrumbsComponent: { type: String, default: 'Breadcrumbs' }, // specify your own globally registered component
  loginVisible: { type: Boolean, default: true }, // if user is not logged in, should we show the login inputs
  checkMaintenanceNotifications: { type: Boolean, default: false },
});

const emit = defineEmits(['title-click']);
const display = useDisplay();
const userSession = useUserSessionStore();

const maintenanceNoticesPeriodicApiCall = ref<number | undefined>(undefined);
const maintenanceNotificationItem = ref<any>(null);

const darkOrLightMode = computed(() => (props.darkMode ? 'dark' : undefined));

const clickLogo = () => {
  window.location.href = '/';
};

const computeTitle = () => {
  if (props.title) {
    if (props.adjustDocumentTitle) document.title = props.title;
    return props.title;
  }

  if (props.adjustDocumentTitle) {
    document.title = props.pageTitle ?
      `${props.pageTitle} - ${userSession.selectedProjectName || ''}` :
      userSession.selectedProjectName;
  }
  return props.pageTitle || 'Project Base Demo';
};

const monitorMaintenanceNotifications = () => {
  maintenanceNoticesPeriodicApiCall.value = setInterval(() => {
    // TODO: this needs to be moved to a separate maintenance-notice import
    if (userSession.loggedIn) {
      apiClient.get(API_CONFIG.MAINTENANCE_NOTIFICATIONS_CONFIG.url, { hideErrorNotice: true })
        .then((notificationResponse: any) => {
          // eslint-disable-next-line no-underscore-dangle,@typescript-eslint/naming-convention
          const _notification: any = _.first(notificationResponse.data);
          if (_notification) {
            const acknowledgeData = _notification.notification_acknowledged_data;
            const delayed = _notification.delayed_to;
            const hours8Range = [delayed - 10 * 3600, (delayed - 2 * 3600) - 1];
            const hours1Range = [delayed - 2 * 3600, (delayed - 10 * 60) - 1];
            const minutes5Range = [delayed - 10 * 60, delayed];
            const now = Math.floor(Date.now() / 1000);
            let rangeIdentifier = 8;
            const hours8 = _.inRange(now, hours8Range[0], hours8Range[1]) &&
                  !_.size(_.filter(acknowledgeData, (v) => v === 8));
            const hours1 = _.inRange(now, hours1Range[0], hours1Range[1]) &&
                  !_.size(_.filter(acknowledgeData, (v) => v === 1));
            const minutes5 = _.inRange(now, minutes5Range[0], minutes5Range[1]) &&
                  !_.size(_.filter(acknowledgeData, (v) => v === 5));
            if (hours1) {
              rangeIdentifier = 1;
            }
            if (minutes5) {
              rangeIdentifier = 5;
            }
            if (!maintenanceNotificationItem.value && (hours8 || hours1 || minutes5)) {
              maintenanceNotificationItem.value = _notification;
              showMaintenanceNotification(maintenanceNotificationItem.value, rangeIdentifier, () => {
                apiClient.post('/maintenance-notification/acknowledged/', {
                  id: maintenanceNotificationItem.value?.id,
                  acknowledged_identifier: rangeIdentifier,
                }).then(() => {
                  document.dispatchEvent(MaintenanceNotificationAcknowledged);
                });
              });
            }
          }
        })
        .catch();
    }
  }, 45000) as unknown as number;
};

onMounted(async () => {
  if (await userSession.checkLogin(false) === true && props.checkMaintenanceNotifications) {
    monitorMaintenanceNotifications();
  }
});

onUnmounted(() => {
  clearInterval(maintenanceNoticesPeriodicApiCall.value);
  maintenanceNoticesPeriodicApiCall.value = undefined;
});
</script>

<style scoped>
.logo-image {
  max-height: 60px;
  max-width: 60px;
}
</style>
