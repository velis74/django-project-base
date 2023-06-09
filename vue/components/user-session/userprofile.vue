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
      await new ConsumerLogicApi('/account/profile/current').dialogForm(null);
    },
    async changePassword() {
      await new ConsumerLogicApi('/account/change-password/').dialogForm('new');
    },
    async handleSocialConnection(e) {
      console.log(
        e,
        e.target.id,
        e.currentTarget,
        e.currentTarget.id,
      );
      // document.getElementById(e.currentTarget.id).style = this.getSocialConnectionStyle(e.currentTarget.id);
      if (!this.isSocialConnectionEnabled(e.currentTarget.id)) {
        console.log(`opening link for ${e.currentTarget.id}`);
        window.location.href = _.first(
          _.filter(this.availableSocialConnections, (conn) => conn.name === e.currentTarget.id),
        ).url;
      }
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

          dfModal.message(gettext('Social connection settings'), () => [
            h('div', { class: 'sc-login-list' }, socAccConfig),
          ]);
        }
      }));
      console.log('edit user social connections');
    },
    getSocialConnectionStyle(name: String) {
      console.log(name, 'getSocialConnectionStyle');
      // TODO: enable disabled
      if (this.isSocialConnectionEnabled(name)) {
        return 'width: 2em; height: 2em; margin: 0 0.2em;';
      }
      return 'width: 2em; height: 2em; margin: 0 0.2em; opacity: 0.4;';
    },
    isSocialConnectionEnabled(name: String) {
      console.log(name, 'isSocialConnectionEnabled');
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
</style>
