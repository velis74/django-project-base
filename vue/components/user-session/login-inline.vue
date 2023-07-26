<template>
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
</template>

<script setup lang="ts">
import { gettext } from '@velis/dynamicforms';

import useLogin from './login';
import SocialLogos from './social-logos.vue';

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
