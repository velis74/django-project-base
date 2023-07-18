<template>
  <div>
    <v-form @submit.prevent>
      <v-container v-if="payload != null" class="pa-0 ma-0 mt-md-6">
        <v-row>
          <v-col class="d-none d-md-flex">
            <v-text-field
              v-model="payload.login"
              density="compact"
              placeholder="Username"
              @keyup.enter="focusPassword"
            />
          </v-col>
          <v-col class="d-none d-md-flex">
            <v-text-field
              ref="pwd"
              v-model="payload.password"
              density="compact"
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
          <v-col class="d-flex">
            <v-btn color="primary" variant="tonal" @click.stop="doLogin">{{ gettext('Login') }}</v-btn>
          </v-col>
          <v-col class="d-none d-md-flex">
            <v-btn color="primary" variant="tonal" @click.stop="openRegistration">{{ gettext('Register') }}</v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-form>
    <df-dialog v-model="showLoginDialog" :size="DialogSize.SMALL">
      <template #title>
        <div>{{ formDef.title }}</div>
      </template>
      <template #body>
        <div>
          <p>
            {{ gettext(`Please sign in with one of your existing third party accounts. Or, `) }}
            <span
              style="text-decoration: underline;
              cursor: pointer"
              tabindex="0"
              @keyup.enter="newAccount()"
              @click.stop="newAccount()"
            >
              {{ gettext(`create a new account`) }}
            </span>
            {{ interpolate(gettext(`for %(appname)s and sign in below:`), { appname }) }}
          </p>
          <div class="text-center my-6">
            <a v-for="(b, bidx) in socialAuth" :key="bidx" :href="b.url" :aria-label="b.title" class="d-inline-block">
              <social-logos :social-provider="b.name" :title="b.title"/>
            </a>
          </div>
          <p class="text-center my-2">{{ gettext('or') }}</p>
          <v-divider/>
          <df-form-layout
            class="my-4"
            :layout="formDef.layout"
            :payload="payload"
            :actions="formDef.actions"
            :errors="errors"
          />
        </div>
      </template>
      <template #actions>
        <div>
          <df-actions :actions="formDef.actions.formFooter"/>
        </div>
      </template>
    </df-dialog>
  </div>
</template>

<script setup lang="ts">
import {
  ConsumerLogicApi,
  DialogSize,
  FormPayload,
  gettext,
  interpolate,
  DisplayMode,
  dfModal as dfModalApi,
  FilteredActions,
  Action, dfModal,
} from '@velis/dynamicforms';
import { AxiosError } from 'axios';
import _ from 'lodash';
import { h, reactive, Ref, ref } from 'vue';

import { apiClient } from '../../apiClient';

import SocialLogos from './social-logos.vue';
import useUserSessionStore from './state';

const userSession = useUserSessionStore();
const loginConsumer = new ConsumerLogicApi(userSession.apiEndpointLogin);

const payload: Ref<FormPayload | null> = ref(null);
const socialAuth = ref([]) as Ref<any[]>;
const pwd = ref();
const formDef = reactive({} as any); // as APIConsumer.FormDefinition
const errors = reactive({} as { [key: string]: any[] });
const resetPasswordErrors = reactive({} as { [key: string]: any[] });
const showLoginDialog = ref(false);
// TODO: needs to be moved to /rest/about or to some configuration. definitely needs to be app-specific
const appname = gettext('Demo app');

let resetPasswordData = { user_id: 0, timestamp: 0, signature: '' };

async function actionResetPassword() {
  showLoginDialog.value = false;
  const resetEmailPromise = await dfModal.message('', () => [
    // eslint-disable-next-line vue/max-len
    h('div', { style: 'display: flex; flex-direction: row; padding-top: 0.3em; padding-bottom: 1em; justify-content: space-around;' }, [
      h('h4', gettext('Enter your e-mail')),
    ]),
    h('div', {}, [
      h('input', {
        type: 'text',
        id: 'input-reset-email',
        style: 'border: 1px black; border-style: solid; border-radius: 5px; ' +
            'width: 100%; margin-bottom: 0.3em; padding: 0.1em;',
      }, {}),
    ]),
  ], new FilteredActions({
    cancel: new Action({
      name: 'cancel',
      label: gettext('Cancel'),
      icon: 'thumbs-down-outline',
      displayStyle: { asButton: true, showLabel: true, showIcon: true },
      position: 'FORM_FOOTER',
    }),
    confirm: new Action({
      name: 'confirm',
      label: gettext('Confirm'),
      icon: 'thumbs-up-outline',
      displayStyle: { asButton: true, showLabel: true, showIcon: true },
      position: 'FORM_FOOTER',
    }),
  }));
  if (resetEmailPromise.action.name === 'confirm') {
    const email: String | null = (<HTMLInputElement>document.getElementById('input-reset-email')).value;
    apiClient.post('/account/send-reset-password-link/', { email }).then((res) => {
      resetPasswordData = res.data;
      window.location.hash = '#reset-user-password';
      enterResetPasswordData();
    });
  }
}

async function getFormDefinition() {
  userSession.checkLogin(false);
  _.assignIn(formDef, await loginConsumer.getFormDefinition());
  payload.value = formDef.payload;
  formDef.layout.fields.social_auth_providers.setVisibility(DisplayMode.SUPPRESS);
  formDef.actions.actions.cancel.actionCancel = () => {
    showLoginDialog.value = false;
  };
  formDef.actions.actions.submit.actionSubmit = () => {
    doLogin();
    showLoginDialog.value = false;
  };
  formDef.actions.actions['reset-password'].actionResetPassword = actionResetPassword;
  socialAuth.value = formDef.payload.social_auth_providers;
}

getFormDefinition();

async function resetUserState() {
  const modalMessageReset = await dfModalApi.message(
    gettext('Account reactivation'),
    () => [
      h(
        'h5',
        {},
        gettext('Your account will be restored. Do you want to keep all your previous data or do ' +
                'you want to reset account state and begin as account was just ' +
                'registered and your previous data is deleted?'),
      ),
    ],
    new FilteredActions({
      confirm: new Action({
        name: 'confirm',
        label: gettext('Reset account'),
        icon: 'thumbs-down-outline',
        displayStyle: { asButton: true, showLabel: true, showIcon: true },
        position: 'FORM_FOOTER',
      }),
      cancel: new Action({
        name: 'cancel',
        label: gettext('Cancel'),
        icon: 'thumbs-up-outline',
        displayStyle: { asButton: true, showLabel: true, showIcon: true },
        position: 'FORM_FOOTER',
      }),
    }),
    { size: DialogSize.SMALL },
  );
  const payload = { reset: false };
  if (modalMessageReset.action.name === 'confirm') {
    payload.reset = true;
  }
  await apiClient.post('/account/profile/reset-user-data', payload).then(() => {
    window.location.reload();
  });
}

function parseErrors(apiErr: AxiosError, errsStore: { [key: string]: any[] }) {
  Object.keys(errsStore).forEach((key: string) => {
    delete errsStore[key];
  });
  // @ts-ignore
  if (apiErr && apiErr.response.data.detail) errsStore.non_field_errors = [apiErr.response.data.detail];
  // @ts-ignore
  else Object.assign(errsStore, apiErr.response.data);
}

async function doLogin() {
  if (payload.value?.login || payload.value?.password) {
    const result = await userSession.login(payload.value?.login, payload.value?.password);
    if (result?.status === 200) {
      // nothing to do: login was a success
      if (userSession.deleteAt) {
        await resetUserState();
      }
      return;
    }
    if (result?.response?.status === 400) {
      parseErrors(result, errors);
    } else {
      Object.keys(errors).forEach((key: string) => {
        delete errors[key];
      });
      errors.non_field_errors = [gettext('Unknown error trying to login')];
    }
  }
  showLoginDialog.value = true;
}

function focusPassword() {
  pwd.value.focus();
}

const newAccount = async () => {
  showLoginDialog.value = false;
  /* TODO show the create account dialog */
  await openRegistration();
};
const openRegistration = async () => {
  await new ConsumerLogicApi('/account/profile/register/', true).dialogForm(null, null, false);
};

async function enterResetPasswordData() {
  if (_.includes(window.location.hash, '#reset-user-password')) {
    const resetEmailPromise = await dfModal.message('', () => [
      // eslint-disable-next-line vue/max-len
      h('div', { style: 'display: flex; flex-direction: row; padding-top: 0.3em; padding-bottom: 1em; justify-content: space-around;' }, [
        h('h4', `${gettext('Please provide new password')}\n\n
        ${gettext('\'Link for password reset was sent to provided e-mail address')}`),
      ]),
      h('div', {}, [
        h('input', {
          type: 'text',
          placeholder: resetPasswordErrors.password ? resetPasswordErrors.password : gettext('New password'),
          id: 'password-reset-input',
          class: 'password-reset-fields',
        }, {}),
        h('input', {
          type: 'text',
          placeholder: resetPasswordErrors.password_confirm ? resetPasswordErrors.password_confirm : gettext(
            'New password confirmation',
          ),
          id: 'password-reset-input-confirmation',
          class: 'password-reset-fields',
        }, {}),
        h('input', {
          type: 'text',
          placeholder: resetPasswordErrors.code ? resetPasswordErrors.code : gettext('Email code'),
          id: 'password-reset-input-code',
          class: 'password-reset-fields',
        }, {}),
      ]),
    ], new FilteredActions({
      cancel: new Action({
        name: 'cancel',
        label: gettext('Cancel'),
        icon: 'thumbs-down-outline',
        displayStyle: { asButton: true, showLabel: true, showIcon: true },
        position: 'FORM_FOOTER',
      }),
      confirm: new Action({
        name: 'reset',
        label: gettext('Reset'),
        icon: 'thumbs-up-outline',
        displayStyle: { asButton: true, showLabel: true, showIcon: true },
        position: 'FORM_FOOTER',
      }),
    }));
    if (resetEmailPromise.action.name === 'reset') {
      const password: String | null = (<HTMLInputElement>document.getElementById('password-reset-input')).value;
      const passwordConfirmation: String | null = (<HTMLInputElement>document.getElementById(
        'password-reset-input-confirmation',
      )).value;
      apiClient.post('/account/reset-password/', {
        user_id: resetPasswordData.user_id,
        timestamp: resetPasswordData.timestamp,
        signature: resetPasswordData.signature,
        password,
        password_confirm: passwordConfirmation,
        code: (<HTMLInputElement>document.getElementById('password-reset-input-code')).value,
      }).then(() => {
        window.location.hash = '';
        dfModal.message('', gettext('Password was reset successfully'));
      }).catch((err) => {
        parseErrors(err, resetPasswordErrors);
        enterResetPasswordData();
      });
      return;
    }
    window.location.hash = '';
  }
}
</script>

<script lang="ts">
export default { name: 'LoginInline' };
</script>

<style>
.v-text-field {
  min-width: 10em;
}

.password-reset-fields {
  border: 1px black;
  border-style: solid;
  border-radius: 5px;
  width: 100%;
  margin-bottom: 0.3em;
  padding: 0.1em;
}

input.password-reset-fields {
  text-align: center;
}
</style>
