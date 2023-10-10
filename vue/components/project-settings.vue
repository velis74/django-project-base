<script setup lang="ts">
import { APIConsumer, ComponentDisplay, ConsumerLogicApi } from '@velis/dynamicforms';
import _ from 'lodash';
import { storeToRefs } from 'pinia';
import { onMounted, onUnmounted, Ref, ref, watch } from 'vue';
import { useCookies } from 'vue3-cookies';

import { apiClient } from '../apiClient';

import { PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME } from './user-session/data-types';
import useUserSessionStore from './user-session/state';

const userSession = useUserSessionStore();
const settingsLogic = ref(new ConsumerLogicApi('/project-settings', false));
const settingsLogicTC = <Ref><unknown> settingsLogic;

const { selectedProjectId } = storeToRefs(userSession);

function refreshSettingsLogic() {
  settingsLogic.value.getFullDefinition();
  settingsLogic.value.reload();
}

if (selectedProjectId.value) refreshSettingsLogic();

const { cookies } = useCookies();

interface ProjectSetting {
  [PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]: any;
  value: string;
  pending_value: string;
  name: string;
}

function confirmationEmail(setting: ProjectSetting) {
  console.log('mail setting', setting);
  console.log('confirm email');
}

function confirmationSms(setting: ProjectSetting) {
  console.log('sms setting', setting);
  console.log('confirm sms');
}

function confirmSetting(setting: ProjectSetting) {
  if (setting.name === 'sms-sender-id') {
    confirmationSms(setting);
    return;
  }
  if (setting.name === 'email-sender-id') {
    confirmationEmail(setting);
  }
}

watch(selectedProjectId, refreshSettingsLogic);
let intervalCheckPendingChanges: NodeJS.Timeout | undefined;
onMounted(() => {
  intervalCheckPendingChanges = setInterval(() => {
    const cookie = cookies.get('setting-verification');
    if (_.size(cookie) && _.size(cookie.split(','))) {
      apiClient.get(`project-settings/${_.first(cookie.split(','))}`).then((res) => {
        console.log(res.data);
        confirmSetting(res.data);
      });
    }
  }, 2500);
});

onUnmounted(() => clearInterval(intervalCheckPendingChanges));

</script>

<template>
  <div class="overflow-y-auto">
    <APIConsumer
      :consumer="settingsLogicTC"
      :display-component="ComponentDisplay.TABLE"
    />
  </div>
</template>
