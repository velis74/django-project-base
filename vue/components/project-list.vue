<script setup lang="ts">
import _ from 'lodash';
import { onMounted, Ref, ref, watch } from 'vue';

import { apiClient as ApiClient } from '../apiClient';
import { PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME } from '../constants';
import { projectSelected as ProjectSelected } from '../events';
import { showNotification } from '../notifications';
import ProjectBaseData from '../projectBaseData';
import { Store } from '../store';

import useUserSessionStore from './user-session/state';

const userSession = useUserSessionStore();

interface ProjectListItem {
  [PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]: any;
  logo: string;
  name: string;
}

const projectList = ref([]) as Ref<ProjectListItem[]>;
const permissions = ref({});
const dataStore = new ProjectBaseData();

function projectSelected(slug: string) {
  if (slug === Store.get('current-project')) return;
  const project = _.first(_.filter(
    projectList,
    (p: ProjectListItem) => p[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME] === slug,
  ));
  Store.set('current-project', project);
  document.dispatchEvent(ProjectSelected);
}

async function getProjects(): Promise<ProjectListItem[]> {
  if (!userSession.loggedIn) return [];
  try {
    return (await ApiClient.get('/project')).data;
  } catch (error: any) {
    console.error(error);
    return [];
  }
}

function setPermissions(newPermissions: {}) {
  permissions.value = newPermissions;
}

async function loadData() {
  if (!userSession.loggedIn) return;
  projectList.value = await getProjects();
  //  WE DO NOT HAVE CURRENT PROJECT FOR USER IMPLEMENTED, FOR NOW WE SKIP THIS
  // if (!Store.get('current-project')) {
  //   Store.set('current-project', _.first(this.projectList)[this.projectTablePkName]);
  //   document.dispatchEvent(ProjectSelected);
  // }

  dataStore.getPermissions(setPermissions);
}

function addNewProject() {
  showNotification('Make project', 'TODO');
}

onMounted(() => { loadData(); });
watch(() => userSession.loggedIn, () => { loadData(); });
</script>

<template>
  <v-btn style="min-width: 0">
    &#9776;
    <v-menu activator="parent">
      <v-list>
        <v-list-item
          v-for="project in projectList"
          :key="project[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]"
          @click="projectSelected(project[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME])"
        >
          <v-img :src="project.logo" class="project-link-image"/>{{ project.name }}
        </v-list-item>
        <v-divider/>
        <v-list-item v-if="permissions['add-project']" @click="addNewProject">
          {{ gettext('Add new project') }}
        </v-list-item>
      </v-list>
    </v-menu>
  </v-btn>
</template>

<style scoped>
.project-link-image {
  max-height: 30px;
  max-width: 30px;
}
</style>
