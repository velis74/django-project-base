<template>
  <div>
    <v-form @submit.prevent>
      <v-container v-if="payload != null">
        <v-row>
          <v-col>
            <v-text-field
              v-model="payload.username"
              density="compact"
              placeholder="Username"
              @keyup.enter="focusPassword"
            />
          </v-col>
          <v-col>
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
            <div :style="`margin-top: .5em; width: ${socialAuth.length * 1.5 * 1.2}em`">
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
import { APIConsumerLogic, DialogSize, FormPayload, gettext, interpolate, DisplayMode } from '@velis/dynamicforms';
import _ from 'lodash';
import { reactive, Ref, ref } from 'vue';

import SocialLogos from './social-logos.vue';
import useUserSessionStore from './state';

const userSession = useUserSessionStore();
const loginConsumer = new APIConsumerLogic(userSession.apiEndpointLogin);

const payload: Ref<FormPayload | null> = ref(null);
const socialAuth = ref([]) as Ref<any[]>;
const pwd = ref();
const formDef = reactive({} as APIConsumer.FormDefinition);
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
  // console.log(formDef);
  // console.log(loginConsumer.ux_def);
  // console.log(payload);
  socialAuth.value = formDef.payload.social_auth_providers;
}
getFormDefinition();

async function doLogin() {
  if (payload.value?.login || payload.value?.password) {
    const result = await userSession.login(payload.value?.login, payload.value?.password);
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
function newAccount() { showLoginDialog.value = false; /* TODO show the create account dialog */ }
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
