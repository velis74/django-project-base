<template>
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
</template>

<script setup lang="ts">
import { APIConsumerLogic, dfModal, DialogSize, FormPayload, gettext } from 'dynamicforms';
import { markRaw, Ref, ref } from 'vue';

import LoginDialog from './login-dialog.vue';
import SocialLogos from './social-logos.vue';
import useUserSessionStore from './state';

const userSession = useUserSessionStore();
const loginConsumer = new APIConsumerLogic(userSession.apiEndpointLogin);

const payload: Ref<FormPayload | null> = ref(null);
const socialAuth = ref([]) as Ref<any[]>;
const pwd = ref();

async function getFormDefinition() {
  userSession.checkLogin(false);
  const formDef = await loginConsumer.getFormDefinition();
  payload.value = formDef.payload;
  console.log(formDef);
  console.log(loginConsumer.ux_def);
  console.log(payload);
  socialAuth.value = formDef.payload.social_auth_providers;
}
getFormDefinition();

async function doLogin() {
  if (payload.value?.username && payload.value?.password) {
    userSession.login(payload.value.username, payload.value.password);
  } else {
    const title = ref(gettext('Sign In'));
    const payload = new FormPayload();
    const body = {
      componentName: markRaw(LoginDialog),
      props: { payload, title },
    };
    await dfModal.message(title, body, undefined, { size: DialogSize.MEDIUM });
    console.log(payload);
  }
}

function focusPassword() { pwd.value.focus(); }
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
