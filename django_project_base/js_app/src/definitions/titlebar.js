/* eslint-disable  import/prefer-default-export */
/* eslint-disable arrow-parens */
/* eslint-disable max-len */
/* eslint-disable no-underscore-dangle */
/* eslint-disable prefer-template */
import _ from 'lodash';
import { Store } from '../store';
import { breadcrumbs } from './breadcrumbs';
import { projectList } from './projectList';
import { login } from './login';
import { userProfile } from './userProfile';
import { apiClient as ApiClient } from '../apiClient';
import { showMaintenanceNotification } from '../notifications';

const titlebar = {
  id: 'titlebar',
  type: 'x-template',
  definition: {
    template: '#titlebar',
    props: {
      darkMode: {
        default: false,
        type: Boolean,
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
      this.loggedIn = Store.get('current-user') !== null && Store.get('current-user') !== undefined;
      this.loadData();
      document.addEventListener('login', (payload) => {
        if (payload.detail) {
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
    mounted() {
    },
    computed: {},
    methods: {
      loadData() {
        if (Store.get('redirect-to-auth')) {
          return;
        }
        this.loadProjectData();
      },
      loadProjectData() {
        if (Store.get('current-project')) {
          ApiClient.get('/project/' + Store.get('current-project')).then(projectResponse => {
            this.titleBarProps = projectResponse.data;
          });
        }
      },
      monitorMaintenanceNotifications() {
        this.maintenanceNoticesPeriodicApiCall = setInterval(() => {
          if (Store.get('current-user')) {
            ApiClient.get('/maintenance-notification/').then(notificationResponse => {
              const _notification = _.first(notificationResponse.data);
              if (_notification) {
                const acknowledgeData = _notification.notification_acknowledged_data;
                const delayed = _notification.delayed_to_timestamp;
                const hours8Range = [delayed - 10 * 3600, (delayed - 2 * 3600) - 1];
                const hours1Range = [delayed - 2 * 3600, (delayed - 10 * 60) - 1];
                const minutes5Range = [delayed - 10 * 60, delayed];
                const now = Math.floor(Date.now() / 1000);
                let rangeIdentifier = 8;
                const hours8 = _.inRange(now, hours8Range[0], hours8Range[1]) && !_.size(_.filter(acknowledgeData, v => v === 8));
                const hours1 = _.inRange(now, hours1Range[0], hours1Range[1]) && !_.size(_.filter(acknowledgeData, v => v === 1));
                const minutes5 = _.inRange(now, minutes5Range[0], minutes5Range[1]) && !_.size(_.filter(acknowledgeData, v => v === 5));
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
  },
  childComponentsDefinition: [
    breadcrumbs, projectList, login, userProfile,
  ],
};

export { titlebar };
