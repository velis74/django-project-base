<template>
  <div v-cloak class="nav-item login-container login-component">
    <div>
      <form class="form-inline" @submit.prevent>
        <input
          v-model="loginModel['username']"
          type="text"
          class="form-control btn-sm"
          placeholder="Username"
          name="username"
          @keyup.enter="focusPassword"
        >
        <input
          v-model="loginModel['password']"
          type="password"
          class="form-control btn-sm mx-1"
          placeholder="Password"
          name="psw"
          @keyup.enter="makeLogin"
        >
        <button
          v-if="socialAuth.length"
          type="button"
          class="btn btn-sm dropdown-toggle"
          data-toggle="dropdown"
          aria-haspopup="true"
          aria-expanded="false"
        />
        <button type="button" class="btn btn-sm btn-primary" @click="makeLogin">
        <!--          {{ gettext('Login') }}-->
          {{ 'Login' }}
        </button>
        <div v-if="socialAuth.length" class="dropdown-menu">
          <a v-for="(b, bidx) in socialAuth" :key="bidx" class="dropdown-item" :href="b.url">{{ b.title }}</a>
        </div>
      </form>
    </div>
    <notification v-if="addNotificationsComponent" position="top center"/>
  </div>
</template>

<script>
import { apiClient as ApiClient } from '../../apiClient';
import { Session } from '../../session';
import { Store } from '../../store';
// import Notification from '../notification.vue';

export default {
  name: 'Login',
  props: {
    addNotificationsComponent: {
      type: Boolean,
      default: true,
    },
  },
  // components: {
  //   Notification,
  // },
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
.form-control {
  height: inherit;
}
.login-container {
  position: absolute;
  right: 1em;
}
</style>
