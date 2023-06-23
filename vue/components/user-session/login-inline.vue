<template>
  <div>
    <v-form @submit.prevent>
      <v-container v-if="payload != null">
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
          <v-col>
            <div :style="`margin-top: .5em; width: ${socialAuth.length * 1.5 * 1.2}em`" class="d-none d-md-flex">
              <a v-for="(b, bidx) in socialAuth" :key="bidx" :href="b.url" :aria-label="b.title" class="d-inline-block">
                <social-logos :social-provider="b.name" :title="b.title" :size-em="1.5"/>
              </a>
            </div>
          </v-col>
          <v-col>
            <v-btn color="primary" variant="tonal" @click.stop="doLogin">{{ gettext('Login') }}</v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-form>
    <df-modal v-model="showLoginDialog" :size="DialogSize.SMALL">
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
    </df-modal>
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
  Action,
} from '@velis/dynamicforms';
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
const showLoginDialog = ref(false);
// TODO: needs to be moved to /rest/about or to some configuration. definitely needs to be app-specific
const appname = gettext('Demo app');

async function getFormDefinition() {
  userSession.checkLogin(false);
  _.assignIn(formDef, await loginConsumer.getFormDefinition());
  payload.value = formDef.payload;
  formDef.layout.fields.social_auth_providers.setVisibility(DisplayMode.SUPPRESS);
  formDef.actions.actions.cancel.actionCancel = () => { showLoginDialog.value = false; };
  formDef.actions.actions.submit.actionSubmit = () => { doLogin(); showLoginDialog.value = false; };
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
      Object.keys(errors).forEach((key: string) => { delete errors[key]; });
      if (result.response.data.detail) errors.non_field_errors = [result.response.data.detail];
      else Object.assign(errors, result.response.data);
    } else {
      Object.keys(errors).forEach((key: string) => { delete errors[key]; });
      errors.non_field_errors = [gettext('Unknown error trying to login')];
    }
  }
  showLoginDialog.value = true;
}

function focusPassword() { pwd.value.focus(); }
const newAccount = async () => {
  showLoginDialog.value = false;
  /* TODO show the create account dialog */
  await new ConsumerLogicApi('/account/profile/', false).dialogForm('new', null, false);
};
</script>

<script lang="ts">
export default { name: 'LoginInline' };
</script>

<style scoped>
.v-container {
  margin-top: 1em;
}

.v-text-field {
  min-width: 10em;
}
</style>
