<script setup lang="ts">
import {
  Action,
  apiClient,
  dfModal,
  FormConsumerApiOneShot,
  FormPayload,
} from '@velis/dynamicforms';
import slugify from 'slugify';
import { onMounted, Ref, ref, watch } from 'vue';

import { Project, PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME } from './data-types';
import useUserSessionStore from './state';

const userSession = useUserSessionStore();
const projectList = ref([]) as Ref<Project[]>;

interface ProjectListProps {
  location: 'top' | 'bottom' | 'left' | 'right' | 'start' | 'end' | 'center';
}

const props = withDefaults(defineProps<ProjectListProps>(), { location: 'bottom' });

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

async function loadData() {
  if (!userSession.loggedIn) return;
  projectList.value = await getProjects();
}

async function addNewProject() {
  // const addProjectModal = await FormConsumerApiOneShot('/project', false, 'new');
  let slugChanged = false;
  let ignoreSlugChange = false;
  const valueChangedHandler = (action: Action, payload: FormPayload, context: any) => {
    if (context.field === 'name' && !slugChanged) {
      payload.slug = slugify(payload.name);
      ignoreSlugChange = true;
    } else if (context.field === 'slug') {
      if (!ignoreSlugChange) slugChanged = true;
      ignoreSlugChange = false;
      if (!payload.slug) slugChanged = false;
    }
    return false;
  };
  const addProjectModal = await FormConsumerApiOneShot(
    '/project',
    false,
    'new',
    undefined,
    { value_changed: valueChangedHandler },
  );
  dfModal.getDialogDefinition(addProjectModal);
  await loadData();
}

onMounted(() => { loadData(); });
watch(() => userSession.loggedIn, () => { loadData(); });
</script>

<script lang="ts">
export default { name: 'ProjectList' };
</script>

<template>
  <v-btn variant="text" style="min-width: 0">
    &#9776; {{ userSession.selectedProject?.name ?? gettext('No Project') }}
    <v-menu activator="parent" :location="props.location">
      <v-list>
        <v-list-item
          v-for="project in projectList"
          :key="project[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]"
          @click="projectSelected(project[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME])"
        >
          <v-img :src="project.logo" class="project-link-image"/>{{ project.name }}
        </v-list-item>
        <v-divider/>
        <v-list-item v-if="userSession.userHasPermission('add-project')" @click="addNewProject">
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
