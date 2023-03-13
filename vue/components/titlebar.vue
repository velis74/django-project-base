<template>
  <v-toolbar :theme="darkOrLightMode">
    <v-toolbar-title v-if="titleBarProps.name || titleBarProps.logo" class="navbar-brand" style="cursor: default;">
      <img
        v-if="titleBarProps.logo"
        alt=""
        :src="titleBarProps.logo"
        class="float-left rounded-circle logo-image"
        onclick="window.location.href='/'"
      />
      {{ titleBarProps.name || '' }}
    </v-toolbar-title>
    <Breadcrumbs v-if="breadcrumbsComponent && userSession.loggedIn"/>
    <v-spacer/>
    <ProjectList v-if="projectlistComponent && userSession.loggedIn"/>
    <UserProfile v-if="userprofileComponent && userSession.loggedIn"/>
    <Login v-else-if="!userSession.loggedIn && loginVisible"/>
    <app-notification/>
  </v-toolbar>
</template>

<script lang="ts">
import _ from 'lodash';
import { defineComponent } from 'vue';

import { apiClient as ApiClient } from '../apiClient';
import { API_CONFIG } from '../apiConfig';
import { maintenanceNotificationAcknowledged as MaintenanceNotificationAcknowledged } from '../events';
import { showMaintenanceNotification } from '../notifications';
import { Store } from '../store';

import Breadcrumbs from './bootstrap/breadcrumbs.vue';
import AppNotification from './notification.vue';
import Login from './user-session/login.vue';
import ProjectList from './user-session/project-list.vue';
import useUserSessionStore from './user-session/state';
import UserProfile from './user-session/userprofile.vue';

export default defineComponent({
  name: 'TitleBar',
  components: {
    AppNotification,
    Breadcrumbs,
    Login,
    ProjectList,
    UserProfile,
  },
  props: {
    darkMode: { type: Boolean, default: false }, // dark mode on when true
    projectlistComponent: { type: String, default: 'ProjectList' }, // specify your own globally registered component
    userprofileComponent: { type: String, default: 'UserProfile' }, // specify your own globally registered component
    breadcrumbsComponent: { type: String, default: 'Breadcrumbs' }, // specify your own globally registered component
    loginVisible: { type: Boolean, default: true }, // if user is not logged in, should we show the login inputs
  },
  data() {
    return {
      titleBarProps: {} as any,
      maintenanceNoticesPeriodicApiCall: null as any,
      maintenanceNotificationItem: null as any,
      userSession: useUserSessionStore(),
    };
  },
  computed: {
    darkOrLightMode() {
      return this.darkMode ? 'dark' : undefined;
    },
  },
  unmounted() {
    clearInterval(this.maintenanceNoticesPeriodicApiCall);
    this.maintenanceNoticesPeriodicApiCall = null;
  },
  async mounted() {
    const userSession = useUserSessionStore();
    if (await userSession.checkLogin(false) === true) {
      if (document.title) {
        // TODO: soon to be removed. This handles situation where titlebar is the only vue component on a legacy page
        this.titleBarProps.name = document.title;
      }
      this.loadData();
      this.monitorMaintenanceNotifications();
    }
  },
  methods: {
    async loadData() {
      if (Store.get('current-project')) {
        const projectResponse = await ApiClient.get(`/project/${Store.get('current-project')}`);
        this.titleBarProps = projectResponse.data;
      }
    },
    monitorMaintenanceNotifications() {
      this.maintenanceNoticesPeriodicApiCall = setInterval(() => {
        // TODO: this needs to be moved to a separate maintenance-notice import
        if (Store.get('current-user')) {
          ApiClient.get(API_CONFIG.MAINTENANCE_NOTIFICATIONS_CONFIG.url, { hideErrorNotice: true })
            .then((notificationResponse) => {
              // eslint-disable-next-line no-underscore-dangle,@typescript-eslint/naming-convention
              const _notification: any = _.first(notificationResponse.data);
              if (_notification) {
                const acknowledgeData = _notification.notification_acknowledged_data;
                const delayed = _notification.delayed_to_timestamp;
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
                if (!this.maintenanceNotificationItem && (hours8 || hours1 || minutes5)) {
                  this.maintenanceNotificationItem = _notification;
                  showMaintenanceNotification(this.maintenanceNotificationItem, rangeIdentifier, () => {
                    ApiClient.post('/maintenance-notification/acknowledged/', {
                      id: this.maintenanceNotificationItem.id,
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
      }, 45000);
    },
  },
});
</script>

<style scoped>
.logo-image {
  max-height: 60px;
  max-width:  60px;
}
</style>