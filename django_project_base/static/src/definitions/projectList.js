import {Store} from '../store';
import _ from 'lodash';
import {translationData} from '../translations';
import {TitleBarData} from '../apps/titlebar/titlebarData';
import {showNotification} from '../notifications';
import {projectSelected as ProjectSelected} from '../events';


const projectListComponentDefinition = {
  defaultId: 'project-list',
  definition: {
    mixins: [projectListMixin], // jshint ignore:line
    data() {
      return {
        projectList: [],
        translations: {},
        permissions: {},
        dataStore: new TitleBarData(),
      };
    },
    created() {
      this.translations = translationData;
      if (Store.get('current-user')) {
        this.loadData();
      }
      document.addEventListener('login', () => {
        this.loadData();
      });
    },
    mounted() {

    },
    computed: {},
    methods: {
      projectSelected(pk) {
        if (pk === Store.get('current-project').id) {
          return;
        }
        Store.set('current-project', _.first(_.filter(this.projectList, p => p.id = pk)));
        document.dispatchEvent(ProjectSelected);
      },
      loadData() {
        this.dataStore.getProjects(this.setProjects);
        this.dataStore.getPermissions(this.setPermissions);
      },
      setProjects(projectList) {
        this.projectList = projectList;
      },
      setPermissions(permissions) {
        this.permissions = permissions;
      },
      addNewProject() {
        showNotification('Make project', 'TODO');
      },
    },
  }
};

export {projectListComponentDefinition};