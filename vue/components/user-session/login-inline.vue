<template>
  <v-form @submit.prevent>
    <v-container v-if="payload != null" class="pa-0 ma-0 mt-md-0">
      <v-row>
        <v-col class="d-none d-md-flex">
          <v-text-field
            :key="loginCredentials"
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
            :key="loginCredentials"
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
          <v-btn color="primary" variant="tonal" @click.stop="loginClick">{{ gettext('Login') }}</v-btn>
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
import { gettext } from '@velis/dynamicforms';
import _ from 'lodash-es';
import { onMounted, ref } from 'vue';
// eslint-disable-next-line import/no-extraneous-dependencies
import { useCookies } from 'vue3-cookies';
import { useDisplay } from 'vuetify';

import { useLogin } from './login';
import SocialLogos from './social-logos.vue';
import useUserSessionStore from './state';
import { accountRegisterVisible } from './use-login-dialog';

const loginCredentials = ref(0);
const { smAndDown } = useDisplay();

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

const usernamePlaceholder = gettext('Username');
const passwordPlaceholder = gettext('Password');

async function openRegistrationForm() {
  await openRegistration();
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

function loginClick() {
  if (smAndDown.value) {
    // Username and password fields are not visible on smaller screens. So we are acting like there is nothing entered.
    // There was a problem where the browser self-fills credentials.
    // And you were not able to se username and password values
    if (payload.value) {
      payload.value.login = '';
      payload.value.password = '';
      loginCredentials.value += 1;
    }
  }
  doLogin();
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
</style>
