<script setup lang="ts">

import {
  DialogSize,
  gettext,
  interpolate,
} from '@velis/dynamicforms';
import { ref, watch } from 'vue';

import { useLogin } from './login';
import SocialLogos from './social-logos.vue';
import { showLoginDialog, accountRegisterVisible } from './use-login-dialog';
// TODO: needs to be moved to /rest/about or to some configuration. definitely needs to be app-specific
const appname = gettext('{put application name here}');

const showDialog = ref<boolean>(false);

const {
  errors,
  payload,
  formDef,
  socialAuth,
  actionResetPassword,
  getFormDefinition,
  newAccount,
} = useLogin();

watch(showLoginDialog, async (newValue) => {
  if (showDialog.value !== newValue) {
    if (!formDef.actions) {
      await getFormDefinition();
    }
    showDialog.value = newValue;
  }
});

</script>

<template>
  <df-dialog v-model="showDialog" :size="DialogSize.SMALL">
    <template #title>
      <div>{{ formDef.title }}</div>
    </template>
    <template #body>
      <div>
        <div v-if="socialAuth.length > 0">
          <p>{{ gettext('Please sign in with') }}</p>
          <div class="text-center my-6">
            <a v-for="(b, bidx) in socialAuth" :key="bidx" :href="b.url" :aria-label="b.title" class="d-inline-block">
              <social-logos :social-provider="b.name" :title="b.title"/>
            </a>
          </div>
          <p class="text-center my-2">{{ gettext('or') }}</p>
          <v-divider/>
        </div>
        <div v-if="accountRegisterVisible">
          <p>
            <span
              style="text-decoration: underline; cursor: pointer"
              tabindex="0"
              @keyup.enter="newAccount()"
              @click.stop="newAccount()"
            >
              {{ gettext('Create a new account') }}
            </span>
            {{ interpolate(gettext(`for %(appname)s and sign in below:`), { appname }) }}
          </p>
          <p class="text-center my-2">{{ gettext('or') }}</p>
          <v-divider/>
        </div>
        <df-form-layout
          class="my-4"
          :layout="formDef.layout"
          :payload="payload"
          :actions="formDef.actions"
          :errors="errors"
        />
        <p
          style="cursor: pointer"
          class="mt-n8 text-decoration-underline"
          @keyup.enter="actionResetPassword"
          @click.stop="actionResetPassword"
        >
          {{ gettext('Forgot password?') }}
        </p>
      </div>
    </template>
    <template #actions>
      <div>
        <df-actions :actions="formDef.actions.formFooter"/>
      </div>
    </template>
  </df-dialog>
</template>
