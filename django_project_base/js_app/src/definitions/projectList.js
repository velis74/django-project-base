/* eslint-disable import/prefer-default-export */
/* eslint-disable arrow-parens */
/* eslint-disable function-paren-newline */
/* eslint-disable prefer-template */
/* eslint-disable no-shadow */
import _ from 'lodash';
import { Store } from '../store';
import { ProjectBaseData } from '../projectBaseData';
import { showNotification } from '../notifications';
import { projectSelected as ProjectSelected } from '../events';
import { PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME } from '../constants';

const projectList = {
  id: 'project-list',
  type: 'x-template',
  definition: {
    template: '#project-list',
    data() {
      return {
        projectList: [],
        permissions: {},
        dataStore: new ProjectBaseData(),
      };
    },
    created() {
      if (Store.get('current-user')) {
        this.loadData();
      }
      document.addEventListener('login', () => {
        this.loadData();
      });
    },
    mounted() {

    },
    computed: {
      projectTablePkName() {
        return PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME;
      },
    },
    methods: {
      projectSelected(slug) {
        if (slug === Store.get('current-project')) {
          return;
        }
        Store.set('current-project', _.first(_.filter(this.projectList,
          p => p[this.projectTablePkName] === slug),
        )[this.projectTablePkName]);
        showNotification(null, 'project ' + slug + ' selected');
        document.dispatchEvent(ProjectSelected);
      },
      loadData() {
        this.dataStore.getProjects(this.setProjects);
        this.dataStore.getPermissions(this.setPermissions);
      },
      setProjects(projectList) {
        this.projectList = projectList;
        if (!Store.get('current-project')) {
          Store.set('current-project', _.first(this.projectList)[this.projectTablePkName]);
          document.dispatchEvent(ProjectSelected);
        }
      },
      setPermissions(permissions) {
        this.permissions = permissions;
      },
      addNewProject() {
        showNotification('Make project', 'TODO');
      },
    },
  },
};

export { projectList };
