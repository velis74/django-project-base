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
        <v-list-item v-if="!userSession.deleteAt" @click="removeMyAccount">
          {{ gettext('Terminate my account') }}
        </v-list-item>
        <v-list-item @click="userSession.logout()">{{ gettext('Logout') }}</v-list-item>
      </v-list>
    </v-menu>
  </v-btn>
</template>

<script lang="ts">
import {
  Action,
  ConsumerLogicApi,
  dfModal,
  DialogSize,
  FilteredActions,
  gettext,
} from '@velis/dynamicforms';
import { defineComponent, h } from 'vue';

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
    async removeMyAccount() {
      const modalMessage = await dfModal.message(
        gettext('Terminate account'),
        () => [
          h(
            'h5',
            {},
            gettext('Your account will be suspended, and all of your data will be ' +
                'permanently deleted after a period of 1 year. Once your account is suspended, you will ' +
                'have the option to reactivate it. If you wish to delete your account ' +
                'immediately, please contact us using the provided information in our contacts.'),
          ),
        ],
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
        { size: DialogSize.SMALL },
      );
      if (modalMessage.action.name === 'confirm') {
        await apiClient.delete(this.userSession.apiEndpointCurrentProfile).then(() => {
          window.location.reload();
        });
      }
    },
  },
});
</script>
