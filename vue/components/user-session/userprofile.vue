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
      socialConnectionModalVisible: false,
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
    async oAuth(e) {
      console.log(e, e.target.id);
    },
    async editSocialConnections() {
      console.log('edit user social connections');
      this.socialConnectionModalVisible = true;
      // type DialogSectionContent = string | Slot | RenderFunction | VNode;
      dfModal.message(gettext('Social connection settings'), () => [
        h('div', { class: 'sc-login-list' }, [
          h(
            'svg',
            {
              innerHTML: icons['google-oauth2'],
              style: 'width: 2em; height: 2em; margin: 0 0.2em;',
              onClick: this.oAuth,
              id: 'google-oauth2',
            },
          ),
          h('svg', { innerHTML: icons.facebook, style: 'width: 2em; height: 2em; margin: 0 0.2em;' }),
        ]),
      ]);
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
