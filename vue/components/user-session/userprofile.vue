<template>
  <v-btn>
    <v-img v-if="userSession.userData.avatar" :src="userSession.userData.avatar"/>
    <h5 v-if="userSession.userDisplayName" class="d-inline-block">
      {{ userSession.userDisplayName }}
      <span v-if="userSession.impersonated">
        ({{ gettext('Impersonated') }})
      </span>
    </h5>

    <v-menu activator="parent">
      <v-list>
        <v-list-item @click="userProfile">{{ gettext('User profile') }}</v-list-item>
        <v-list-item @click="changePassword">{{ gettext('Change password') }}</v-list-item>

        <v-list-item
          v-if="permissions['impersonate-user'] && !userSession.impersonated"
          @click="showImpersonateLogin"
        >
          {{ gettext('Impersonate user') }}
        </v-list-item>

        <v-list-item v-if="userSession.impersonated" @click="stopImpersonation">
          {{ gettext('Stop impersonation') }}
        </v-list-item>
        <v-divider/>
        <v-list-item @click="editSocialConnections">{{ gettext('Edit social connections') }}</v-list-item>
        <v-list-item @click="userSession.logout()">{{ gettext('Logout') }}</v-list-item>
      </v-list>
    </v-menu>
  </v-btn>
</template>

<script lang="ts">
import { ConsumerLogicApi, dfModal, gettext } from '@velis/dynamicforms';
import axios from 'axios';
import _ from 'lodash';
import { defineComponent, h } from 'vue';
import IonIcon from 'vue-ionicon';

import { apiClient } from '../../apiClient';
import ProjectBaseData from '../../projectBaseData';

import icons from './icons';
import useUserSessionStore from './state';

export default defineComponent({
  name: 'UserProfile',
  // eslint-disable-next-line vue/no-unused-components
  components: { IonIcon },
  data() {
    return {
      permissions: {} as any,
      userSession: useUserSessionStore(),
      enabledSocialConnections: [],
      availableSocialConnections: [],
    };
  },
  mounted() {
    this.loadData();
  },
  methods: {
    async loadData(force: boolean = false) {
      new ProjectBaseData().getPermissions((p: any) => {
        this.permissions = p;
      });
      if (this.userSession.loggedIn && !force) {
        await this.checkResetPassword();
        return;
      }
      await this.userSession.checkLogin(false);
      await this.checkResetPassword();
    },
    async checkResetPassword() {
      if (this.userSession.passwordInvalid) {
        await this.changePassword();
      }
    },
    async showImpersonateLogin() {
      await new ConsumerLogicApi('/account/impersonate').dialogForm(null);
      await this.userSession.checkLogin(false);
    },
    async stopImpersonation() {
      await apiClient.delete('/account/impersonate');
      await this.userSession.checkLogin(false);
    },
    async userProfile() {
      await new ConsumerLogicApi('/account/profile', false).dialogForm(this.userSession.userId);
      await this.userSession.checkLogin(false);
    },
    async changePassword() {
      await new ConsumerLogicApi('/account/change-password/').dialogForm('new');
    },
    async handleSocialConnection(e) {
      if (!this.isSocialConnectionEnabled(e.currentTarget.id)) {
        window.location.href = _.first(
          _.filter(this.availableSocialConnections, (conn) => conn.name === e.currentTarget.id),
        ).url;
      }
    },
    mergeUsers(e) {
      e.preventDefault();
      const user: String | null = document.getElementById('merge-user-user').value;
      const passwd: String | null = document.getElementById('merge-user-password').value;
      const account: Boolean | null = document.getElementById('merge-user-account').checked;
      apiClient.post('/account/profile/merge-accounts', { login: user, password: passwd, account }).then((response) => {
        console.log(response.data);
      });
    },
    async editSocialConnections() {
      axios.all([
        apiClient.get('account/social-auth-providers'),
        apiClient.get('account/social-auth-providers-user'),
      ]).then(axios.spread((available, used) => {
        this.enabledSocialConnections = used.data;
        this.availableSocialConnections = available.data;
        if (_.size(available.data)) {
          const socAccConfig = _.map(this.availableSocialConnections, (socAcc) => (
            h('div', {
              innerHTML: icons[socAcc.name],
              style: this.getSocialConnectionStyle(socAcc.name),
              onClick: this.handleSocialConnection,
              id: socAcc.name,
              'data-url': socAcc.url,
            })));
          dfModal.message('', () => [
            h('div', { style: 'display: flex; flex-direction: row; padding-top: 0.3em; padding-bottom: 1em; justify-content: space-around;' }, [
              h('h4', gettext('Social connections')),
            ]),
            h('div', {}, [
              h('div', { class: 'sc-login-list' }, socAccConfig),
              h('div', { class: 'merge-accounts' }, [
                h('h4', gettext('Merge account with following credentials')),
                h('div', { style: 'display: flex; flex-direction: column; align-items: center;' }, [
                  h('div', { class: 'merge-accounts', style: 'display: flex; flex-direction: column;' }, [
                    h('div', { class: 'div-input' }, [
                      h('label', {}, gettext('Username or email')),
                      h('input', { type: 'text', class: 'merge-user-input', id: 'merge-user-user' }, {}),
                    ]),
                    h('div', { class: 'div-input' }, [
                      h('label', {}, gettext('Password')),
                      h('input', { type: 'text', class: 'merge-user-input', id: 'merge-user-password' }, {}),
                    ]),
                    h('div', { style: '' }, [
                      h('label', {}, gettext('Currently logged in user account will be main account')),
                      h('input', { type: 'checkbox', class: 'merge-user-input', id: 'merge-user-account' }, {}),
                    ]),

                  ]),
                  // TODO: add check for added sc login
                  // TODO: validate merge users
                  // TODO: execute merge users
                  h('button', {
                    onClick: this.mergeUsers,
                    style: 'margin-top: 0.3em; width: 20%; background-color: #ABEBC6;',
                    class: 'merge-user-input',
                  }, 'Merge'),

                ]),
              ]),
            ]),
          ]);
          return;
        }
        dfModal.message(gettext('Social connections'), gettext('No social connections available'));
      }));
    },
    getSocialConnectionStyle(name: String) {
      // TODO: enable disabled
      if (this.isSocialConnectionEnabled(name)) {
        return 'width: 2em; height: 2em; margin: 0 0.2em;';
      }
      return 'width: 2em; height: 2em; margin: 0 0.2em; opacity: 0.4;';
    },
    isSocialConnectionEnabled(name: String) {
      return _.includes(_.map(this.enabledSocialConnections, 'provider'), name);
    },
  },
});
</script>
<style>
.sc-login-list {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  flex-wrap: wrap;
}

.merge-accounts {
  display: flex;
  flex-direction: column;
  margin-top: 2em;
}

.merge-user-input {
  border: 1px black;
  border-style: solid;
  border-radius: 5px;
}

.div-input {
  display: flex; flex-direction: row;
  margin-bottom: 0.3em;
}

.div-input > * { flex: 1; }
</style>
