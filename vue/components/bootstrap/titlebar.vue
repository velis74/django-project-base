<template>
  <div v-cloak class="titlebar-app titlebar-component">
    <nav class="navbar navbar-expand-lg" :class="darkOrLightMode">
      <div v-if="titleBarProps.name || titleBarProps.logo" class="navbar-brand" style="cursor: default;">
        <img
          v-if="titleBarProps.logo"
          alt=""
          :src="titleBarProps.logo"
          class="float-left rounded-circle logo-image"
          onclick="window.location.href='/'"
        />
        {{ titleBarProps.name || '' }}
      </div>
      <div v-if="breadcrumbsComponent && loggedIn">
        <Breadcrumbs/>
      </div>
      <div class="collapse navbar-collapse mr-auto"/>
      <div v-if="projectlistComponent && loggedIn" class="collapse navbar-collapse">
        <ul class="navbar-nav"/>
        <ProjectList/>
      </div>
      <div v-if="userprofileComponent && loggedIn">
        <UserProfile/>
      </div>
      <div v-else-if="!loggedIn && loginVisible" class="login">
        <Login :add-notifications-component="false"/>
      </div>
    </nav>
    <!--    <notification/>-->
  </div>
</template>

<script lang="ts">
import _ from 'lodash';

import { apiClient as ApiClient } from '../../apiClient';
import { API_CONFIG } from '../../apiConfig';
import { maintenanceNotificationAcknowledged as MaintenanceNotificationAcknowledged } from '../../events';
import { showMaintenanceNotification } from '../../notifications';
import { Session } from '../../session';
import { Store } from '../../store';
// import Notification from '../notification.vue';

import Breadcrumbs from './breadcrumbs.vue';
import Login from './login.vue';
import ProjectList from './projectlist.vue';
import UserProfile from './userprofile.vue';

export default {
  name: 'TitleBar',
  components: {
    // Notification,
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
      titleBarProps: {},
      loggedIn: null,
      lightClass: 'navbar-light bg-light',
      darkClass: 'navbar-dark bg-dark',
      maintenanceNoticesPeriodicApiCall: null,
      maintenanceNotificationItem: null,
    };
  },
  computed: {
    darkOrLightMode() {
      return this.darkMode ? this.darkClass : this.lightClass;
    },
  },
  beforeDestroy() {
    clearInterval(this.maintenanceNoticesPeriodicApiCall);
    this.maintenanceNoticesPeriodicApiCall = null;
  },
  created() {
    Session.checkLogin(false, this.createdCallback);
  },
  methods: {
    createdCallback() {
      if (document.title) {
        this.titleBarProps.name = document.title;
      }
      this.loggedIn = Store.get('current-user') !== null && Store.get('current-user') !== undefined;
      this.loadData();
      document.addEventListener('login', (payload) => {
        if (payload.detail && payload.detail['default-project']) {
          this.titleBarProps = payload.detail['default-project'];
        } else {
          this.loadData();
        }
        this.loggedIn = true;
      });
      document.addEventListener('logout', () => {
        this.loggedIn = null;
        this.titleBarProps = {};
      });
      document.addEventListener('project-selected', () => {
        this.loadData();
      });
      document.addEventListener('maintenance-notification-acknowledged', () => {
        this.maintenanceNotificationItem = null;
      });
      this.monitorMaintenanceNotifications();
    },
    loadData() {
      this.loadProjectData();
    },
    loadProjectData() {
      if (Store.get('current-project')) {
        ApiClient.get(`/project/${Store.get('current-project')}`).then((projectResponse) => {
          this.titleBarProps = projectResponse.data;
        });
      }
    },
    monitorMaintenanceNotifications() {
      this.maintenanceNoticesPeriodicApiCall = setInterval(() => {
        if (Store.get('current-user')) {
          ApiClient.get(API_CONFIG.MAINTENANCE_NOTIFICATIONS_CONFIG.url,
            { hideErrorNotice: true }).then((notificationResponse) => {
            // eslint-disable-next-line no-underscore-dangle,@typescript-eslint/naming-convention
            const _notification = _.first(notificationResponse.data);
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
          }).catch();
        }
      }, 45000);
    },
  },
};
</script>

<style scoped>
.titlebar-app .card, .nav-item > .card > .card-body {
  border: none;
  padding: 0;
  cursor: pointer;
}

.logo-image {
  max-height: 60px;
  max-width: 60px;
}

.login {
  min-height: 2em;
}
</style>
