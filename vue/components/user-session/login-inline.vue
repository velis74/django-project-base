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
            placeholder="Username"
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
            placeholder="Password"
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
        <v-col class="d-none d-md-flex mt-1 mr-2">
          <v-btn color="primary" variant="tonal" @click.stop="openRegistrationForm">{{ gettext('Register') }}</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
import { Action, dfModal, FilteredActions, gettext } from '@velis/dynamicforms';
import _ from 'lodash';
import { h, onMounted } from 'vue';
// eslint-disable-next-line import/no-extraneous-dependencies
import { useCookies } from 'vue3-cookies';

import useLogin from './login';
import SocialLogos from './social-logos.vue';
import useUserSessionStore from './state';

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

async function openRegistrationForm() {
  let registration = await openRegistration();
  console.log('registerd', registration);
  registration = true;
  if (registration) {
    const okDialog = await dfModal.message(
      '',
      gettext('New account registration dialog is filled out and confirmed successfully. ' +
        'the account itself is made inactive with delete_at set to +24 hours.'),
      new FilteredActions({
        confirm: new Action({
          name: 'confitm',
          label: gettext('Ok'),
          displayStyle: { asButton: true, showLabel: true, showIcon: true },
          position: 'FORM_FOOTER',
        }),
      }),
    );

    console.log('ok ko', okDialog);

    const userEmailChoice = await dfModal.message('', () => [
      h(
        'h3',
        { class: 'd-flex justify-center mb-4' },
        [gettext('New account')],
      ),
      h(
        'h4',
        { class: 'd-flex justify-center mb-4' },
        [`${gettext('We have sent an email to the email address you provided.')}`],
      ),
      h(
        'h4',
        { class: 'd-flex justify-center mb-4' },
        [`${gettext('Please enter the code from the message')}:`],
      ),
      h('div', { class: 'd-flex justify-center mb-4' }, [
        h('input', {
          type: 'text',
          // placeholder: resetPasswordErrors.code ? resetPasswordErrors.code : gettext('Email code'),
          id: 'new-account-confirmation-code',
          class: 'w-20 mb-2 p-1 justify-center rounded border-lightgray',
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
    console.log('user email choice', userEmailChoice);
    if (userEmailChoice.action.name === 'proceed') {
      console.log(userEmailChoice);
      // send code for verification
      const pageName = userSession.selectedProjectName || '';
      dfModal.message(
        gettext('New account'),
        gettext('Your account is now active and you are logged in.') + (
          _.size(pageName) ? gettext('Welcome to') + pageName : ''),
      );

      return;
    }
    console.log('DIFFERENT EMAIL');
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
