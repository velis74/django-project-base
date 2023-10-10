<script setup lang="ts">
import {
  Action,
  APIConsumer,
  ComponentDisplay,
  ConsumerLogicApi,
  dfModal,
  FilteredActions,
  gettext,
} from '@velis/dynamicforms';
import _ from 'lodash';
import { storeToRefs } from 'pinia';
import { onMounted, onUnmounted, Ref, ref, watch, h } from 'vue';
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

const settingsConfirmationVisible = ref(false);

async function confirmationEmail(setting: ProjectSetting, message: Array<any>) {
  console.log('mail setting', setting);
  console.log('confirm email');
  if (settingsConfirmationVisible.value) {
    return;
  }
  settingsConfirmationVisible.value = true;
  const emailConfirmation = await dfModal.message('', () => message, new FilteredActions({
    cancel: new Action({
      name: 'cancel',
      label: gettext('Cancel'),
      displayStyle: { asButton: true, showLabel: true, showIcon: true },
      position: 'FORM_FOOTER',
    }),
    confirm: new Action({
      name: 'confirm',
      label: gettext('I haved confirmed pending setting'),
      displayStyle: { asButton: true, showLabel: true, showIcon: true },
      position: 'FORM_FOOTER',
    }),
  }));
  if (emailConfirmation.action.name === 'confirm') {
    apiClient.post(
      '/project-settings/confirm-setting',
      { PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME: setting[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME] },
    ).then((res) => {
      console.log(res.data);
      console.log('confirmation respnse');
    });
  }
  settingsConfirmationVisible.value = false;
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
    confirmationEmail(setting, [
      h('h2', { class: 'mt-n6 mb-4' }, gettext('Email settings pending for confirmation')),
      h('br'),
      h('h4', { class: 'mt-n6 mb-4' }, gettext('You received an email with confirmation link ' +
        'for email sender address. Please check your mail and click on confirmation link. Check also spam folder ' +
        'if you do not find confirmation link.')),
    ]);
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
