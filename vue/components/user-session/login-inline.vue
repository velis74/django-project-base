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
          <v-btn color="primary" variant="tonal" @click.stop="openRegistration">{{ gettext('Register') }}</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
import { gettext } from '@velis/dynamicforms';
import _ from 'lodash';
import { onMounted } from 'vue';
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
const userSession = useUserSessionStore();

function focusPassword() {
  pwd.value.focus();
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
