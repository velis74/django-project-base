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

        <v-list-item v-if="permissions['is-staff-user']" @click="addUser">
          {{ gettext('Add user') }}
        </v-list-item>

        <v-list-item v-if="userSession.impersonated" @click="stopImpersonation">
          {{ gettext('Stop impersonation') }}
        </v-list-item>
        <v-divider/>
        <v-list-item @click="removeMyAccount">
          {{ gettext('Terminate my account') }}
        </v-list-item>
        <v-list-item @click="userSession.logout()">{{ gettext('Logout') }}</v-list-item>
      </v-list>
    </v-menu>
  </v-btn>
</template>

<script lang="ts">
import { Action, ConsumerLogicApi, defaultActionHandler, dfModal, FilteredActions, gettext } from '@velis/dynamicforms';
import { defineComponent } from 'vue';

import { apiClient } from '../../apiClient';
import ProjectBaseData from '../../projectBaseData';

import useUserSessionStore from './state';

export default defineComponent({
  name: 'UserProfile',
  data() {
    return {
      permissions: {} as any,
      userSession: useUserSessionStore(),
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
    async addUser() {
      await new ConsumerLogicApi('/account/admin-add-user/').dialogForm('new');
    },
    async removeMyAccount() {
      const modalM = await dfModal.message(
        gettext('Title'),
        gettext('Message'),
        new FilteredActions({
          confirm: new Action({
            name: 'confirm',
            label: gettext('Confirm'),
            icon: 'thumbs-up-outline',
            displayStyle: { asButton: true, showLabel: true, showIcon: true },
            position: 'FORM_FOOTER',
          }),
          cancel: new Action({
            name: 'cancel',
            label: gettext('Cancel'),
            icon: 'thumbs-down-outline',
            displayStyle: { asButton: true, showLabel: true, showIcon: true },
            position: 'FORM_FOOTER',
          }),
        }),
      );
      console.log(modalM);
      await apiClient.delete(this.userSession.apiEndpointCurrentProfile);
    },
  },
});
</script>
