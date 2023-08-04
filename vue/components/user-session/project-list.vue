<script setup lang="ts">
import { apiClient, ConsumerLogicApi, dfModal } from '@velis/dynamicforms';
import { onMounted, Ref, ref, watch } from 'vue';

import ProjectBaseData from '../../projectBaseData';

import { Project, PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME } from './data-types';
import useUserSessionStore from './state';

interface Permissions {
  [key: string]: unknown;
}

const userSession = useUserSessionStore();

const projectList = ref([]) as Ref<Project[]>;
const permissions = ref({} as Permissions);
const dataStore = new ProjectBaseData();

function projectSelected(slug: string) {
  if (slug === userSession.selectedProjectId) return;
  const project = projectList.value.find((p: Project) => p[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME] === slug);
  userSession.setSelectedProject(project);
}

async function getProjects(): Promise<Project[]> {
  // TODO: this is wrong: anonymousUser has access to all free projects, at least for viewing.
  //  Denoted by "anonymous user" or "external user" in permissions / roles editor
  //  To be clear: what is wrong with the next line is requiring to be logged in before we check for projects
  if (!userSession.loggedIn) return [];
  try {
    return (await apiClient.get('/project')).data;
  } catch (error: any) {
    console.error(error);
    return [];
  }
}

function setPermissions(newPermissions: Permissions) {
  permissions.value = newPermissions;
}

async function loadData() {
  if (!userSession.loggedIn) return;
  projectList.value = await getProjects();
  dataStore.getPermissions(setPermissions);
}

async function addNewProject() {
  const addProjectModal = await new ConsumerLogicApi('/project', false).dialogForm('new');
  await dfModal.getDialogDefinition(addProjectModal);
  await loadData();
}

onMounted(() => { loadData(); });
watch(() => userSession.loggedIn, () => { loadData(); });
</script>

<script lang="ts">
export default { name: 'ProjectList' };
</script>

<template>
  <v-btn style="min-width: 0">
    &#9776; {{ userSession.selectedProject?.name ?? gettext('NO Project') }}
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
