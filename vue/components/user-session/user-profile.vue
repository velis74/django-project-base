<template>
  <v-btn>
    <v-img v-if="userSession.userData.avatar" :src="userSession.userData.avatar"/>
    <h4 v-if="userSession.userDisplayName" class="d-inline-block">
      {{ userSession.userDisplayName }}
      <span v-if="userSession.impersonated">
        ({{ gettext('Impersonated') }})
      </span>
    </h4>

    <v-menu activator="parent">
      <v-list>
        <component :is="props.projectListComponent" v-if="showProjectList" location="start"/>
        <v-divider v-if="showProjectList"/>

        <v-list-item @click="userProfile">{{ gettext('User profile') }}</v-list-item>
        <v-list-item @click="changePassword">{{ gettext('Change password') }}</v-list-item>
        <v-list-item v-if="showAccountSocial" @click="editSocialConnections">
          {{ gettext('Edit social connections') }}
        </v-list-item>

        <v-list-item
          v-if="userSession.userHasPermission('impersonate-user') && !userSession.impersonated"
          @click="showImpersonateLogin"
        >
          {{ gettext('Impersonate user') }}
        </v-list-item>

        <v-list-item v-if="userSession.impersonated" @click="stopImpersonation">
          {{ gettext('Stop impersonation') }}
        </v-list-item>
        <v-divider/>
        <v-list-item v-if="showAccountSocial && !userSession.deleteAt" @click="removeMyAccount">
          {{ gettext('Terminate my account') }}
        </v-list-item>
        <v-list-item @click="userSession.logout()">{{ gettext('Logout') }}</v-list-item>
      </v-list>
    </v-menu>
  </v-btn>
</template>

<script setup lang="ts">
import {
  Action,
  dfModal,
  DfNotifications,
  DialogSize,
  FilteredActions,
  FormConsumerOneShotApi,
  gettext,
  interpolate,
} from '@velis/dynamicforms';
import axios, { AxiosRequestConfig } from 'axios';
import _ from 'lodash-es';
import { computed, h, onMounted, reactive, ref, watch } from 'vue';
import { useCookies } from 'vue3-cookies';
import { useDisplay } from 'vuetify';

import { apiClient } from '../../api-client';
import { HTTP_401_UNAUTHORIZED } from '../../api-config';
import { SocialAccItem } from '../../social-integrations';

import { PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME, UserDataJSON } from './data-types';
import icons from './icons';
import { parseErrors } from './login';
import ProjectList from './project-list.vue'; // eslint-disable-line @typescript-eslint/no-unused-vars
import useUserSessionStore from './state';

type IconObjectKey = keyof typeof icons;

export interface UserProfileProps {
  projectListComponent: string;
}

const { cookies } = useCookies();
const showAccountSocial = ref(false);

const props = withDefaults(defineProps<UserProfileProps>(), { projectListComponent: 'ProjectList' });
const display = useDisplay();
const userSession = useUserSessionStore();
let enabledSocialConnections = [] as Array<SocialAccItem>;
let availableSocialConnections = [] as Array<SocialAccItem>;
let socialConnectionsModalPromise = null as any;

const showProjectList = computed(() => (props.projectListComponent && userSession.loggedIn && display.smAndDown.value));
const changePasswordErrors = reactive({} as { [key: string]: any[] });

async function verifyEmailChanged(userData: UserDataJSON) {
  const verifyMailCookie = cookies.get('verify-email');
  if (_.size(verifyMailCookie) && userData[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME] &&
    userData[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME].toString() === verifyMailCookie.toString()) {
    const enterEmailConfirmationCode = await dfModal.message('Update email', () => [
      h(
        'h4',
        { class: 'mt-n6 mb-4' },
        // eslint-disable-next-line vue/max-len
        interpolate('%(text)s:', { text: gettext('We have sent an email to the new email address you provided. Please enter the code from the message') }),
      ),
      h('div', { style: 'display: flex; justify-content: center;' }, [h('input', {
        type: 'text',
        id: 'input-change-email',
        placeholder: changePasswordErrors.code ? changePasswordErrors.code : gettext('Email code'),
        style: 'padding: 0.1em;',
        class: 'w-50 mb-4 p-2 rounded border-lightgray',
      }, {})]),
    ], new FilteredActions({
      cancel: new Action({
        name: 'cancel',
        label: gettext('Cancel'),
        displayStyle: { asButton: true, showLabel: true, showIcon: true },
        position: 'FORM_FOOTER',
      }),
      confirm: new Action({
        name: 'confirm',
        label: gettext('Confirm'),
        displayStyle: { asButton: true, showLabel: true, showIcon: true },
        position: 'FORM_FOOTER',
      }),
    }));
    if (enterEmailConfirmationCode.action.name === 'confirm') {
      apiClient.post(
        '/account/profile/confirm-new-email',
        { code: (<HTMLInputElement>document.getElementById('input-change-email')).value },
        { hideErrorNotice: true } as AxiosRequestConfig,
      ).then(() => {
        dfModal.message('', gettext('Your new email is now verified, thank you. '));
      }).catch((err: any) => {
        parseErrors(err, changePasswordErrors);
        verifyEmailChanged(userData);
      });
    }
  }
}

async function changePassword() {
  await FormConsumerOneShotApi({ url: '/account/change-password/', trailingSlash: true, pk: 'new' });
}

async function checkResetPassword() {
  if (userSession.passwordInvalid) {
    await changePassword();
  }
}

async function loadData(force: boolean = false) {
  const userData: UserDataJSON = {
    full_name: '',
    email: '',
    username: '',
    avatar: '',
    password_invalid: false,
    is_superuser: false,
    permissions: [],
    is_impersonated: false,
    groups: [],
    delete_at: '',
    [PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME]: '',
  };
  userData[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME] = userSession.userData[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME];
  userData.email = userSession.userData.email;
  if (userSession.loggedIn && !force) {
    await checkResetPassword();
    await verifyEmailChanged(userData);
    return;
  }
  await userSession.checkLogin(false);
  await checkResetPassword();
  await verifyEmailChanged(userData);
}

watch(() => userSession.impersonated, () => window.location.reload());
onMounted(() => loadData());

async function showImpersonateLogin() {
  await FormConsumerOneShotApi({ url: '/account/impersonate', trailingSlash: false });
  await userSession.checkLogin(false);
}

async function stopImpersonation() {
  await apiClient.delete('/account/impersonate');
  await userSession.checkLogin(false);
}

async function userProfile() {
  const savedData = await FormConsumerOneShotApi({ url: '/account/profile/current', trailingSlash: false });
  await userSession.checkLogin(false);
  await verifyEmailChanged(savedData);
}

function isSocialConnectionEnabled(name: String) {
  return _.includes(_.map(enabledSocialConnections, 'provider'), name);
}

async function handleSocialConnection(e: Event) {
  const target = e.currentTarget as HTMLTextAreaElement;
  if (!isSocialConnectionEnabled(target.id)) {
    window.location.href = _.first(
      _.filter(availableSocialConnections, (conn) => conn.name as string === target.id),
    )?.url!;
  }
}

function mergeUsers(e: Event) {
  e.preventDefault();
  const user: String | null = (<HTMLInputElement>document.getElementById('merge-user-user')).value;
  const passwd: String | null = (<HTMLInputElement>document.getElementById('merge-user-password')).value;
  const account: Boolean | null = (<HTMLInputElement>document.getElementById('merge-user-account')).checked;
  apiClient.post(
    '/account/profile/merge-accounts',
    { login: user, password: passwd, account },
    { hideErrorNotice: true },
  ).then(() => {
    if (socialConnectionsModalPromise) {
      dfModal.getDialogDefinition(socialConnectionsModalPromise)?.close();
    }
  }).catch((err: any) => {
    if (err.response.status === HTTP_401_UNAUTHORIZED) {
      if (socialConnectionsModalPromise) {
        dfModal.getDialogDefinition(socialConnectionsModalPromise)?.close();
      }
      window.location.reload();
      return;
    }
    DfNotifications.showNotificationFromAxiosException(err);
  });
}

function getSocialConnectionStyle(name: String) {
  if (isSocialConnectionEnabled(name)) {
    return 'width: 2em; height: 2em; margin: 0 0.2em;';
  }
  return 'width: 2em; height: 2em; margin: 0 0.2em; opacity: 0.2; cursor: grab;';
}

async function editSocialConnections() {
  axios.all([
    apiClient.get('account/social-auth-providers'),
    apiClient.get('account/social-auth-providers-user'),
  ]).then(axios.spread((available, used) => {
    enabledSocialConnections = used.data;
    availableSocialConnections = available.data;
    if (_.size(available.data)) {
      const socAccConfig = _.map(availableSocialConnections, (socAcc) => (
        h('div', {
          innerHTML: icons[socAcc.name as IconObjectKey],
          style: getSocialConnectionStyle(socAcc.name),
          onClick: handleSocialConnection,
          id: socAcc.name,
          'data-url': socAcc.url,
        })));
      socialConnectionsModalPromise = dfModal.message('', () => [
        // eslint-disable-next-line vue/max-len
        h(
          'div',
          {
            style: 'display: flex; flex-direction: row; padding-top: 0.3em; ' +
              'padding-bottom: 1em; justify-content: space-around;',
          },
          [h('h4', gettext('Social connections'))],
        ),
        h('div', {}, [
          h('div', { class: 'sc-login-list' }, socAccConfig),
          h('div', { class: 'merge-accounts' }, [
            h('h4', { style: 'align-self: center;' }, gettext('Merge account with following credentials')),
            h('div', { style: 'display: flex; flex-direction: column; align-items: center;' }, [
              h('div', { class: 'merge-accounts', style: 'display: flex; flex-direction: column;' }, [
                h('div', { class: 'div-input' }, [
                  h('label', {}, gettext('Username or email')),
                  h('input', { type: 'text', class: 'merge-user-input', id: 'merge-user-user' }, {}),
                ]),
                h('div', { class: 'div-input' }, [
                  h('label', {}, gettext('Password')),
                  h('input', { type: 'text', class: 'merge-user-input', id: 'merge-user-password' }, {}),
                ]),
                h('div', { style: '' }, [
                  h('label', {}, gettext('Currently logged in user account will be main account')),
                  h('input', { type: 'checkbox', class: 'merge-user-input', id: 'merge-user-account' }, {}),
                ]),

              ]),
              h('button', {
                onClick: mergeUsers,
                style: 'margin-top: 0.3em; width: 20%; background-color: #ABEBC6;',
                class: 'merge-user-input',
              }, 'Merge'),

            ]),
          ]),
        ]),
      ]);
      return;
    }
    socialConnectionsModalPromise = dfModal.message(
      gettext('Social connections'),
      gettext('No social connections available'),
    );
  }));
}

async function removeMyAccount() {
  const modalMessage = await dfModal.message(
    gettext('Terminate account'),
    () => [
      h(
        'h5',
        {},
        // eslint-disable-next-line vue/max-len
        gettext('Your account will be suspended, and all of your data will be permanently deleted after a period of 1 year. Once your account is suspended, you will have the option to reactivate it. If you wish to delete your account immediately, please contact us using the provided information in our contacts.'),
      ),
    ],
    new FilteredActions({
      confirm: new Action({
        name: 'confirm',
        label: gettext('Confirm'),
        icon: 'ion-thumbs-up-outline',
        displayStyle: { asButton: true, showLabel: true, showIcon: true },
        position: 'FORM_FOOTER',
      }),
      cancel: new Action({
        name: 'cancel',
        label: gettext('Cancel'),
        icon: 'ion-thumbs-down-outline',
        displayStyle: { asButton: true, showLabel: true, showIcon: true },
        position: 'FORM_FOOTER',
      }),
    }),
    { size: DialogSize.SMALL },
  );
  if (modalMessage.action.name === 'confirm') {
    await apiClient.delete(userSession.apiEndpointCurrentProfile).then(() => {
      window.location.reload();
    });
  }
}
</script>

<style>
.sc-login-list {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  flex-wrap: wrap;
}

.merge-accounts {
  display: flex;
  flex-direction: column;
  margin-top: 2em;
}

.merge-user-input {
  border: 1px solid black;
  border-radius: 5px;
}

.div-input {
  display: flex;
  flex-direction: row;
  margin-bottom: 0.3em;
  padding: 0.1em;
}

.div-input input {
  padding: 0.2em;
}

.div-input > * {
  flex: 1;
}
</style>
