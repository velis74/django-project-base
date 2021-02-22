import {Store} from '../store';
import {breadcrumbs} from './breadcrumbs';
import {projectList} from './projectList';
import {login} from './login';
import {userProfile} from './userProfile';
import {apiClient as ApiClient} from '../apiClient';


const titlebar = {
  id: 'titlebar',
  type: 'x-template',
  definition: {
    template: `#titlebar`,
    data() {
      return {
        titleBarProps: {},
        loggedIn: null,
      };
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
    },
    mounted() {
    },
    computed: {},
    methods: {
      loadData() {
        if (Store.get('redirect-to-auth')) {
          return;
        }
        let projectPk = Store.get('current-project');
        if (projectPk === null || projectPk === undefined) {
          ApiClient.get('account/profile/current?decorate=default-project').then(response => {
            Store.set('current-project', response.data['default-project'].id);
            Store.set('current-user', response.data);
            this.titleBarProps = response.data['default-project'];
            this.loggedIn = true;
          });
          return;
        }
        this.loadProjectData();
      },
      loadProjectData() {
        ApiClient.get('project/' + Store.get('current-project')).then(projectResponse => {
          this.titleBarProps = projectResponse.data;
        });
      }
    },
  },
  childComponentsDefinition: [
    breadcrumbs, projectList, login, userProfile
  ],
};

export {titlebar};


