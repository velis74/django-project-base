<template>
  <div class="nav-item project-list-dropdown projectlist-component" v-cloak>
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav">
        <li class="nav-item dropdown">
          <i class="nav-link fas fa-th-list fa-2x" data-toggle="dropdown"></i>
          <div class="dropdown-menu" aria-labelledby="navbarDropdown">
            <a v-for="project in projectList"
               v-on:click="projectSelected(project[projectTablePkName])"
               v-bind:key="project[projectTablePkName]" class="dropdown-item project-item" href="#">
              <img v-bind:src="project.logo" class="project-link-image">{{ project.name }}</a>
            <a v-if="permissions['add-project']" v-on:click="addNewProject"
               class="dropdown-item project-item" href="#">
              <i class="fas fa-plus-circle"></i>{{ gettext('Add new project') }}</a>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import ProjectBaseData from '../../projectBaseData';
import { Store } from '../../store';
import { PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME } from '../../constants';
import { projectSelected as ProjectSelected } from '../../events';
import { showNotification } from '../../notifications';

export default {
  name: 'projectlist',
  data() {
    return {
      projectList: [],
      permissions: {},
      dataStore: new ProjectBaseData(),
      isLoadingData: false,
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
        (p) => p[this.projectTablePkName] === slug))[this.projectTablePkName]);
      document.dispatchEvent(ProjectSelected);
    },
    loadData() {
      if (this.isLoadingData) {
        return;
      }
      this.isLoadingData = true;
      const dataPromise = this.dataStore.getProjects(this.setProjects);
      if (dataPromise) {
        dataPromise.finally(() => {
          this.isLoadingData = false;
        });
      } else {
        this.isLoadingData = false;
      }
      this.dataStore.getPermissions(this.setPermissions);
    },
    setProjects(projectList) {
      this.projectList = projectList;
      //  WE DO NOT HAVE CURRENT PROJECT FOR USER IMPLEMENTED, FOR NOW WE SKIP THIS
      // if (!Store.get('current-project')) {
      //   Store.set('current-project', _.first(this.projectList)[this.projectTablePkName]);
      //   document.dispatchEvent(ProjectSelected);
      // }
    },
    setPermissions(permissions) {
      this.permissions = permissions;
    },
    addNewProject() {
      showNotification('Make project', 'TODO');
    },
  },
};
</script>

<style scoped>
  .project-link-image {
    max-height: 30px;
    max-width: 30px;
  }
</style>
