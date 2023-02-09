<template>
  <div v-cloak class="nav-item project-list-dropdown projectlist-component">
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav">
        <li class="nav-item dropdown">
          <i class="nav-link fas fa-th-list fa-2x" data-toggle="dropdown"/>
          <div class="dropdown-menu" aria-labelledby="navbarDropdown" style="left: -4em;">
            <a
              v-for="project in projectList"
              :key="project[projectTablePkName]"
              class="dropdown-item project-item"
              href="#"
              @click="projectSelected(project[projectTablePkName])"
            >
              <img :src="project.logo" alt="" class="project-link-image">{{ project.name }}</a>
            <a
              v-if="permissions['add-project']"
              class="dropdown-item project-item"
              href="#"
              @click="addNewProject"
            >
              <i class="fas fa-plus-circle"/>{{ gettext('Add new project') }}</a>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import _ from 'lodash';
import { defineComponent } from 'vue';

import { apiClient as ApiClient } from '../../apiClient';
import { PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME } from '../../constants';
import { projectSelected as ProjectSelected } from '../../events';
import { showNotification } from '../../notifications';
import ProjectBaseData from '../../projectBaseData';
import { Store } from '../../store';

export default defineComponent({
  name: 'ProjectList',
  data() {
    return {
      projectList: [] as any[],
      permissions: {},
      dataStore: new ProjectBaseData(),
      isLoadingData: false,
    };
  },
  computed: {
    projectTablePkName() {
      return PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME;
    },
  },
  created() {
    if (Store.get('current-user')) {
      this.loadData();
    }
    document.addEventListener('login', () => {
      this.loadData();
    });
  },
  methods: {
    projectSelected(slug: string) {
      if (slug === Store.get('current-project')) {
        return;
      }
      Store.set('current-project', _.first(_.filter(this.projectList, (p) => p[this.projectTablePkName] === slug)));
      document.dispatchEvent(ProjectSelected);
    },
    getProjects(callback: Function) {
      if (!Store.get('current-user')) {
        return null;
      }
      return ApiClient.get('/project').then((response) => {
        callback(response.data);
      }).catch((error) => {
        callback([]);
        // eslint-disable-next-line no-console
        console.error(error);
      });
    },
    loadData() {
      if (this.isLoadingData) {
        return;
      }
      this.isLoadingData = true;
      const dataPromise = this.getProjects(this.setProjects);
      if (dataPromise) {
        dataPromise.finally(() => {
          this.isLoadingData = false;
        });
      } else {
        this.isLoadingData = false;
      }
      this.dataStore.getPermissions(this.setPermissions);
    },
    setProjects(projectList: any[]) {
      this.projectList = projectList;
      //  WE DO NOT HAVE CURRENT PROJECT FOR USER IMPLEMENTED, FOR NOW WE SKIP THIS
      // if (!Store.get('current-project')) {
      //   Store.set('current-project', _.first(this.projectList)[this.projectTablePkName]);
      //   document.dispatchEvent(ProjectSelected);
      // }
    },
    setPermissions(permissions: any[]) {
      this.permissions = permissions;
    },
    addNewProject() {
      showNotification('Make project', 'TODO');
    },
  },
});
</script>

<style scoped>
.project-link-image {
  max-height: 30px;
  max-width: 30px;
}
</style>
