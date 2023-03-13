<script setup lang="ts">
import _ from 'lodash';
import { onMounted, Ref, ref, watch } from 'vue';

import { apiClient as ApiClient } from '../../apiClient';
import { showNotification } from '../../notifications';
import ProjectBaseData from '../../projectBaseData';

import { Project, PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME } from './data-types';
import useUserSessionStore from './state';

const userSession = useUserSessionStore();

const projectList = ref([]) as Ref<Project[]>;
const permissions = ref({});
const dataStore = new ProjectBaseData();

function projectSelected(slug: string) {
  if (slug === userSession.selectedProjectId) return;
  const project = projectList.value.find((p: Project) => p[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME] === slug);
  userSession.setSelectedProject(project);
}

async function getProjects(): Promise<Project[]> {
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
  if (!userSession.selectedProjectId) userSession.setSelectedProject(_.first(projectList.value));
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
    &#9776; {{ userSession.selectedProject.name }}
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
