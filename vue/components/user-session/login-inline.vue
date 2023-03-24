<template>
  <v-form @submit.prevent>
    <v-container>
      <v-row>
        <v-col>
          <v-text-field
            v-model="loginModel.username"
            density="compact"
            placeholder="Username"
            @keyup.enter="focusPassword"
          />
        </v-col>
        <v-col>
          <v-text-field
            ref="pwd"
            v-model="loginModel.password"
            density="compact"
            type="password"
            placeholder="Password"
            @keyup.enter="doLogin"
          />
        </v-col>
        <v-col>
          <v-btn v-if="socialAuth.length" color="secondary" style="min-width: 0">
            &#9660;
            <v-menu activator="parent">
              <v-list>
                <v-list-item v-for="(b, bidx) in socialAuth" :key="bidx" :href="b.url">
                  {{ b.title }}
                </v-list-item>
              </v-list>
            </v-menu>
          </v-btn>
          <v-btn color="primary" variant="tonal" @click.stop="doLogin">{{ gettext('Login') }}</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
import { dfModal, gettext, DialogSize, FormPayload } from 'dynamicforms';
import { markRaw, onMounted, reactive, Ref, ref } from 'vue';

import { apiClient as ApiClient } from '../../apiClient';

import LoginDialog from './login-dialog.vue';
import useUserSessionStore from './state';

const loginModel = reactive({
  username: null as string | null,
  password: null as string | null,
});
const socialAuth = ref([]) as Ref<any[]>;
const pwd = ref();

async function checkLoginSuccess() {
  const userSession = useUserSessionStore();
  if ([true, 403].includes(await userSession.checkLogin(false))) {
    if (!userSession.loggedIn) {
      const socialAuthProvidersResponse = await ApiClient.get('/account/social-auth-providers/');
      socialAuth.value = socialAuthProvidersResponse.data as any[];
    }
  }
}

async function doLogin() {
  if (loginModel.username && loginModel.password) {
    const userSession = useUserSessionStore();
    userSession.login(loginModel.username, loginModel.password);
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

onMounted(() => checkLoginSuccess());
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
