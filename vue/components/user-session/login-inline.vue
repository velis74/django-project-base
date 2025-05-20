<template>
  <v-form @submit.prevent>
    <v-container v-if="payload != null" class="pa-0 ma-0 mt-md-0">
      <v-row>
        <v-col class="d-none d-md-flex">
          <v-text-field
            v-model="payload.login"
            density="compact"
            single-line
            hide-details
            :placeholder="usernamePlaceholder"
            @keyup.enter="focusPassword"
          />
        </v-col>
        <v-col class="d-none d-md-flex">
          <v-text-field
            ref="pwd"
            v-model="payload.password"
            density="compact"
            single-line
            hide-details
            type="password"
            :placeholder="passwordPlaceholder"
            @keyup.enter="doLogin"
          />
        </v-col>
        <v-col class="d-none d-md-flex">
          <a v-for="(b, no) in socialAuth" :key="no" :href="b.url" :aria-label="b.title" class="d-inline-block mt-2">
            <social-logos :social-provider="b.name" :title="b.title" :size-em="1.5"/>
          </a>
        </v-col>
        <v-col class="d-flex mt-1">
          <v-btn color="primary" variant="tonal" @click.stop="doLogin">{{ gettext('Login') }}</v-btn>
        </v-col>
        <v-col v-if="accountRegisterVisible" class="d-none d-md-flex mt-1">
          <v-btn color="primary" variant="tonal" @click.stop="openRegistrationForm">{{ gettext('Register') }}</v-btn>
        </v-col>
        <v-col class="d-none d-md-flex mt-1 mr-2"/>
      </v-row>
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
import { Action, dfModal, FilteredActions, gettext, interpolate } from '@velis/dynamicforms';
import _ from 'lodash-es';
import { h, onMounted, reactive } from 'vue';
// eslint-disable-next-line import/no-extraneous-dependencies
import { useCookies } from 'vue3-cookies';

import { apiClient } from '../../api-client';

import { parseErrors, useLogin } from './login';
import SocialLogos from './social-logos.vue';
import useUserSessionStore from './state';
import { accountRegisterVisible } from './use-login-dialog';

const {
  payload,
  pwd,
  socialAuth,
  doLogin,
  getFormDefinition,
  openRegistration,
} = useLogin();

getFormDefinition();

function focusPassword() {
  pwd.value.focus();
}

const userSession = useUserSessionStore();

const registerWorkflowErrors = reactive({} as { [key: string]: any[] });

const usernamePlaceholder = gettext('Username');
const passwordPlaceholder = gettext('Password');

async function validateEmailCode() {
  const userEmailChoice = await dfModal.message('', () => [
    h(
      'h3',
      { class: 'd-flex justify-center mb-4' },
      [gettext('New account')],
    ),
    h(
      'h4',
      { class: 'd-flex justify-center mb-4' },
      [gettext('We have sent an email to the email address you provided.')],
    ),
    h(
      'h4',
      { class: 'd-flex justify-center mb-4' },
      [interpolate('%(text)s:', { text: gettext('Please enter the code from the message') })],
    ),
    h('div', { class: 'd-flex justify-center mb-4' }, [
      h('input', {
        type: 'text',
        id: 'new-account-confirmation-code',
        class: 'w-20 mb-2 p-1 justify-center rounded border-lightgray',
        style: 'padding: 0.1em;',
        placeholder: registerWorkflowErrors.code ? registerWorkflowErrors.code : null,
      }, {}),
    ]),
  ], new FilteredActions({
    cancel: new Action({
      name: 'different-email',
      label: gettext('Different email'),
      displayStyle: { asButton: true, showLabel: true, showIcon: true },
      position: 'FORM_FOOTER',
    }),
    confirm: new Action({
      name: 'proceed',
      label: gettext('Proceed'),
      displayStyle: { asButton: true, showLabel: true, showIcon: true },
      position: 'FORM_FOOTER',
    }),
  }));

  const pageName = userSession.selectedProjectName || '';
  if (userEmailChoice.action.name === 'proceed') {
    apiClient.post(
      '/account/verify-registration/',
      { code: (<HTMLInputElement>document.getElementById('new-account-confirmation-code'))?.value },
    ).then(() => {
      registerWorkflowErrors.value = [];
      userSession.checkLogin(false).then(() => {
        dfModal.message(
          gettext('New account'),
          gettext('Your account is now active and you are logged in.') + (
            _.size(pageName) ? gettext('Welcome to') + pageName : ''),
        );
      });
    }).catch((err: any) => {
      parseErrors(err, registerWorkflowErrors);
      validateEmailCode();
    });
    return true;
  }
  return false;
}

async function changeRegisterMail() {
  const userEmail = await dfModal.message('', () => [
    h(
      'h3',
      { class: 'd-flex justify-center mb-4' },
      [interpolate('%(newAccountText) - %{differentMailText}', {
        newAccountText: gettext('New account'),
        differentMailText: gettext('different email'),
      })],
    ),

    h(
      'h4',
      { class: 'd-flex justify-center mb-4' },
      [interpolate('%(text)s:', { text: gettext('Please enter new email') })],
    ),
    h('div', { class: 'd-flex justify-center mb-4' }, [
      h('input', {
        type: 'text',
        id: 'new-account-different-email',
        placeholder: registerWorkflowErrors.email ? registerWorkflowErrors.email : null,
        class: 'w-100 mb-2 p-1 justify-center rounded border-lightgray',
        style: 'padding: 0.1em;',
      }, {}),
    ]),
  ], new FilteredActions({
    cancel: new Action({
      name: 'cancel',
      label: gettext('Cancel'),
      displayStyle: { asButton: true, showLabel: true, showIcon: true },
      position: 'FORM_FOOTER',
    }),
    confirm: new Action({
      name: 'proceed-different-email',
      label: gettext('Proceed'),
      displayStyle: { asButton: true, showLabel: true, showIcon: true },
      position: 'FORM_FOOTER',
    }),
  }));
  if (userEmail.action.name === 'proceed-different-email') {
    apiClient.post(
      '/account/verify-registration-email-change/',
      { email: (<HTMLInputElement>document.getElementById('new-account-different-email'))?.value },
    ).then(() => {
      validateEmailCode();
      registerWorkflowErrors.value = [];
    }).catch((err: any) => {
      parseErrors(err, registerWorkflowErrors);
      changeRegisterMail();
    });
  }
}

async function openRegistrationForm() {
  const registration = await openRegistration();
  if (registration) {
    if (!await validateEmailCode()) {
      await changeRegisterMail();
    }
  }
}

function checkInvite() {
  if (!userSession.loggedIn) {
    const { cookies } = useCookies();
    if (_.size(cookies.get('invite-pk'))) {
      doLogin();
      cookies.remove('invite-pk');
    }
  }
}

onMounted(() => checkInvite());
</script>

<script lang="ts">
export default { name: 'LoginInline' };
</script>

<style>
.v-text-field {
  min-width: 10em;
}

.border-lightgray {
  border: 1px solid lightgrey;
}
</style>
