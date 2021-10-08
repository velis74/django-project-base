<template>
  <div v-cloak class="titlebar-app titlebar-component">
    <nav class="navbar navbar-expand-lg " v-bind:class="[darkMode ? darkClass : lightClass]">
      <div class="nav-item" v-if="titleBarProps.logo">
        <div class="card">
          <div class="card-body">
            <img
              v-bind:src="titleBarProps.logo"
              class="float-left rounded-circle logo-image"
              onclick="window.location.href='/'">
          </div>
        </div>
      </div>
      <div
        class="navbar-brand left-spacing"
        v-if="titleBarProps.name"
        href="javascript:void(0);"
        style="cursor: default;">
        {{ titleBarProps.name }}
      </div>
      <div v-if="breadcrumbsVisible && loggedIn" class="left-spacing">
        <breadcrumbs></breadcrumbs>
      </div>
      <div class="collapse navbar-collapse" v-if="projectlistVisible && loggedIn">
        <ul class="navbar-nav mr-auto">
        </ul>
        <projectlist></projectlist>
      </div>
      <div v-if="userprofileVisible && loggedIn">
        <userprofile></userprofile>
      </div>
      <div v-else-if="!loggedIn && loginVisible" class="login">
        <login></login>
      </div>
    </nav>
    <notifications width="350" position="top center" v-if="loggedIn">
      <template slot="body" slot-scope="{ item, close }">
        <div
          @click="item.data.onNotificationClose(item, close, true)"
          class="vue-notification"
          :class="item.type">
          <div>
            <div style="display: inline-block; max-width: 95%;" class="notification-title">
              <div v-html="item.title"></div>
            </div>
            <div style="display: inline-block; max-width: 95%;" class="notification-content">
              <div v-html="item.text"/>
            </div>
            <div
              style="display: inline-block; float: right; vertical-align: middle;"
              v-if="item.data.duration === -1">
              <button class="close" @click="item.data.onNotificationClose(item, close)">
                <i class="fas fa-times fa-xs"></i>
              </button>
            </div>
          </div>
        </div>
      </template>
    </notifications>
  </div>
</template>

<script>
import _ from 'lodash';

import { apiClient as ApiClient } from '../../apiClient';
import { showMaintenanceNotification } from '../../notifications';
import { Session } from '../../session';
import { Store } from '../../store';

import breadcrumbs from './breadcrumbs.vue';
import login from './login.vue';
import projectlist from './projectlist.vue';
import userprofile from './userprofile.vue';

export default {
  name: 'titlebar',
  props: {
    darkMode: {
      default: false,
      type: Boolean,
    },
    projectlistVisible: {
      type: Boolean,
      default: true,
    },
    userprofileVisible: {
      type: Boolean,
      default: true,
    },
    breadcrumbsVisible: {
      type: Boolean,
      default: true,
    },
    loginVisible: {
      type: Boolean,
      default: true,
    },
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
          ApiClient.get('/maintenance-notification/',
            { hideErrorNotice: true }).then((notificationResponse) => {
            // eslint-disable-next-line no-underscore-dangle
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
                showMaintenanceNotification(this.maintenanceNotificationItem, rangeIdentifier);
              }
            }
          }).catch();
        }
      }, 45000);
    },
  },
  components: {
    breadcrumbs,
    login,
    projectlist,
    userprofile,
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

  .left-spacing {
    margin-left: 1em;
  }

  .login {
    min-height: 2em;
  }
</style>
