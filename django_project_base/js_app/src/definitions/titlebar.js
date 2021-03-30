import {Store} from '../store';
import {breadcrumbs} from './breadcrumbs';
import {projectList} from './projectList';
import {login} from './login';
import {userProfile} from './userProfile';
import {apiClient as ApiClient} from '../apiClient';
import {showMaintenanceNotification} from '../notifications';
import _ from 'lodash';


const titlebar = {
  id: 'titlebar',
  type: 'x-template',
  definition: {
    template: `#titlebar`,
    data() {
      return {
        titleBarProps: {},
        loggedIn: null,
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
          ApiClient.get('project/' + Store.get('current-project')).then(projectResponse => {
            this.titleBarProps = projectResponse.data;
          });
        }
      },
      monitorMaintenanceNotifications() {
        this.maintenanceNoticesPeriodicApiCall = setInterval(() => {
          ApiClient.get('maintenance-notification/').then(notificationResponse => {
            let _notification = _.first(notificationResponse.data);
            let delayed = _notification.delayed_to_timestamp;
            let now = Math.floor(Date.now() / 1000);
            let hours8 = _.inRange(now, delayed - 10 * 3600, delayed - 6 * 3600);
            let hours1 = _.inRange(now, delayed - 2 * 3600, delayed - 0.5 * 3600);
            let minutes5 = _.inRange(now, delayed - 10 * 60, delayed);
            if ((!this.item || this.item.id !== _notification.id) && (hours8 || hours1 || minutes5)) {
              this.maintenanceNotificationItem = _notification;
              showMaintenanceNotification(this.item);
            }
          }).catch();
        }, 45000);
      },
    },
  },
  childComponentsDefinition: [
    breadcrumbs, projectList, login, userProfile
  ],
};

export {titlebar};


