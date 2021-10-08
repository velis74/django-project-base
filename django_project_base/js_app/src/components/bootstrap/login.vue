<template>
  <div class="nav-item login-container login-component" v-cloak>
    <div>
      <form @submit.prevent>
        <input
            type="text"
            v-on:keyup.enter="focusPassword"
            v-model="loginModel['username']"
            placeholder="Username"
            name="username">
        <input
            type="password"
            v-on:keyup.enter="makeLogin"
            v-model="loginModel['password']"
            placeholder="Password"
            name="psw">
        <div class="btn-group dropleft" style="display: inline;">
          <button
              v-if="socialAuth.length"
              type="button"
              class="btn btn-sm dropdown-toggle"
              data-toggle="dropdown"
              aria-haspopup="true"
              aria-expanded="false">
          </button>
          <button type="button" class="btn btn-sm" @click="makeLogin">
            {{ gettext('Login') }}
          </button>
          <div v-if="socialAuth.length" class="dropdown-menu">
            <a v-for="(b, bidx) in socialAuth" class="dropdown-item" :key="bidx" :href="b.url">{{ b.title }}</a>
          </div>
        </div>
      </form>
    </div>
    <notifications position="top center"/>
  </div>
</template>

<script>
import { apiClient as ApiClient } from '../../apiClient';
import { Session } from '../../session';
import { Store } from '../../store';

export default {
  name: 'login',
  data() {
    return {
      loginModel: {
        username: null,
        password: null,
      },
      socialAuth: [],
    };
  },
  mounted() {
    Session.checkLogin(false, this.checkLoginSuccessCallback);
  },
  methods: {
    checkLoginSuccessCallback() {
      if (!Store.get('current-user')) {
        ApiClient.get('/account/social-auth-providers/')
          .then((socProvResponse) => {
            this.socialAuth = socProvResponse.data;
          });
      }
    },
    makeLogin() {
      Session.login(this.loginModel.username, this.loginModel.password);
    },
    focusPassword() {
      document.getElementsByName('psw')[0].focus();
    },
  },
};
</script>

<style scoped>
.login-container {
  position: absolute;
  right: 1em;
}
</style>
