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
            @keyup.enter="makeLogin"
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
          <v-btn color="primary" variant="tonal" @click.stop="makeLogin">{{ gettext('Login') }}</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script lang="ts">
// import { dfModal } from 'dynamicforms';
import { defineComponent } from 'vue';

import { apiClient as ApiClient } from '../apiClient';
import Session from '../session';
import { Store } from '../store';

export default defineComponent({
  // eslint-disable-next-line vue/multi-word-component-names
  name: 'Login',
  data() {
    return {
      loginModel: {
        username: null as string | null,
        password: null as string | null,
      },
      socialAuth: [] as any[],
    };
  },
  mounted() {
    this.checkLoginSuccess();
  },
  methods: {
    async checkLoginSuccess() {
      if ([true, 403].includes(await Session.checkLogin(false))) {
        if (!Store.get('current-user')) {
          const socialAuthProvidersResponse = await ApiClient.get('/account/social-auth-providers/');
          this.socialAuth = socialAuthProvidersResponse.data as any[];
        }
      }
    },
    async makeLogin() {
      if (this.loginModel.username && this.loginModel.password) {
        Session.login(this.loginModel.username, this.loginModel.password);
      } else {
        // await dfModal.message('Error', 'Username and password must both be non-empty!');
      }
    },
    focusPassword() { (<HTMLElement> this.$refs.pwd).focus(); },
  },
});
</script>

<style scoped>
.v-container {
  margin-top: 1em;
}
.v-text-field {
  min-width: 10em;
}
</style>
