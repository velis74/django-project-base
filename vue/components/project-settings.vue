<script setup lang="ts">
import {
  Action,
  APIConsumer,
  ComponentDisplay,
  ConsumerLogicApi,
  dfModal,
  FilteredActions,
  FormPayload,
  gettext,
  interpolate,
  useActionHandler,
} from '@velis/dynamicforms';
import _ from 'lodash-es';
import { storeToRefs } from 'pinia';
import { h, onMounted, onUnmounted, ref, Ref, watch } from 'vue';
import { useCookies } from 'vue3-cookies';

import { apiClient } from '../api-client';

import { PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME } from './user-session/data-types';
import useUserSessionStore from './user-session/state';

const userSession = useUserSessionStore();
const settingsLogic = ref(new ConsumerLogicApi('/project-settings', false));
const settingsLogicTC = <Ref><unknown>settingsLogic;

const { selectedProjectId } = storeToRefs(userSession);

const { cookies } = useCookies();
const hasConsumerDefinition = ref(false);

function refreshSettingsLogic() {
  if (!hasConsumerDefinition.value) {
    settingsLogic.value.getFullDefinition().then(() => {
      hasConsumerDefinition.value = true;
    });
  } else {
    settingsLogic.value.reload();
  }
}

interface ProjectSetting {
  [PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME]: any;
  value: string;
  pending_value: string;
  name: string;
}

const settingsConfirmationVisible = ref(false);

async function confirmationEmail(setting: ProjectSetting, message: Array<any>) {
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
      label: gettext('I have confirmed pending setting'),
      displayStyle: { asButton: true, showLabel: true, showIcon: true },
      position: 'FORM_FOOTER',
    }),
  }));
  const reqData = {};
  // @ts-ignore
  reqData[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME] = setting[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME];
  if (emailConfirmation.action.name === 'confirm') {
    apiClient.post(
      '/project-settings/confirm-setting',
      reqData,
    ).then(() => {
      const cookie = cookies.get('setting-verification');
      if (_.size(cookie)) {
        cookies.set(
          'setting-verification',
          _.join(
            _.filter(cookie.split('*'), (i) => i !== setting[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME].toString()),
            '*',
          ),
        );
      }
      apiClient.get(
        interpolate('/project-settings/%(path)s', { path: setting[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME] }),
      ).then((res: any) => {
        if (_.size(res.data.pending_value)) {
          dfModal.message(
            '',
            // eslint-disable-next-line vue/max-len
            gettext('We have attempted to verify the sender email address, but it doesn\'t work yet. Please click "try again" in about a minute or so'),
            new FilteredActions({
              cancel: new Action({
                name: 'cancel',
                label: gettext('Cancel, use the old sender email'),
                displayStyle: { asButton: true, showLabel: true, showIcon: true },
                position: 'FORM_FOOTER',
              }),
              confirm: new Action({
                name: 'ok',
                label: gettext('OK'),
                displayStyle: { asButton: true, showLabel: true, showIcon: true },
                position: 'FORM_FOOTER',
              }),
            }),
          ).then((action: Action) => {
            if (action.action.name === 'cancel') {
              apiClient.post(
                '/project-settings/reset-pending',
                reqData,
              ).finally(() => {
                refreshSettingsLogic();
                settingsConfirmationVisible.value = false;
              });
              return;
            }
            refreshSettingsLogic();
            settingsConfirmationVisible.value = false;
          });
          return;
        }
        settingsConfirmationVisible.value = false;
      }).catch(() => {
        settingsConfirmationVisible.value = false;
      });
    }).catch(() => {
      settingsConfirmationVisible.value = false;
    });
    return;
  }
  settingsConfirmationVisible.value = false;
}

async function confirmationSms(setting: ProjectSetting, message: Array<any>) {
  if (settingsConfirmationVisible.value) {
    return;
  }
  settingsConfirmationVisible.value = true;
  await dfModal.message('', () => message, new FilteredActions({
    cancel: new Action({
      name: 'ok',
      label: gettext('OK'),
      displayStyle: { asButton: true, showLabel: true, showIcon: true },
      position: 'FORM_FOOTER',
    }),
  }));
  settingsConfirmationVisible.value = false;
}

function confirmSetting(setting: ProjectSetting) {
  if (setting.name === 'sms-sender-id') {
    confirmationSms(setting, [
      h('h2', { class: 'mt-n6 mb-4' }, gettext('SMS settings pending for confirmation')),
      h('br'),
      h(
        'h4',
        { class: 'mt-n6 mb-4' },
        // eslint-disable-next-line vue/max-len
        gettext('Sms sender settings is pending for confirmation. It can take up to two weeks for setting to become active. You will be notified when settings will be activated.'),
      ),
    ]);
    return;
  }
  if (setting.name === 'email-sender-id') {
    confirmationEmail(setting, [
      h('h2', { class: 'mt-n6 mb-4' }, gettext('Email settings pending for confirmation')),
      h('br'),
      h(
        'h4',
        { class: 'mt-n6 mb-4' },
        // eslint-disable-next-line vue/max-len
        gettext('You received an email with confirmation link for email sender address. Please check your mail and click on confirmation link. Check also spam folder if you do not find confirmation link.'),
      ),
    ]);
  }
}

function checkSettings() {
  const cookie = cookies.get('setting-verification');
  if (_.size(cookie) && _.size(cookie.split('*'))) {
    apiClient.get(
      interpolate('/project-settings/%(path)s.json', { path: _.first(cookie.split('*')) }),
    ).then((res: any) => {
      confirmSetting(res.data);
    });
  }
}

let intervalCheckPendingChanges: NodeJS.Timeout | undefined;
onMounted(() => {
  intervalCheckPendingChanges = setInterval(() => {
    checkSettings();
  }, 45000);
});

onUnmounted(() => clearInterval(intervalCheckPendingChanges));

function refreshSettingsLogicAndCheckSettings() {
  refreshSettingsLogic();
  checkSettings();
}

if (selectedProjectId.value) refreshSettingsLogicAndCheckSettings();

watch(selectedProjectId, refreshSettingsLogicAndCheckSettings);

const actionResetPending = async (action: Action, payload: FormPayload) => {
  const resetData = {};
  // @ts-ignore
  resetData[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME] = payload[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME];
  apiClient.post(
    '/project-settings/reset-pending',
    resetData,
  ).then(() => {
    refreshSettingsLogic();
  });
  return true;
};

const actionConfirmSettingActive = async (action: Action, payload: FormPayload) => {
  const activeData = {};
  // @ts-ignore
  activeData[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME] = payload[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME];
  apiClient.post(
    '/project-settings/confirm-setting-active',
    activeData,
  ).then(() => {
    refreshSettingsLogic();
  });
  return true;
};

const { handler } = useActionHandler();

handler
  .register('reset-pending', actionResetPending).register('confirm-setting-active', actionConfirmSettingActive);

</script>

<template>
  <div class="overflow-y-auto">
    <APIConsumer
      :consumer="settingsLogicTC"
      :display-component="ComponentDisplay.TABLE"
    />
  </div>
</template>
