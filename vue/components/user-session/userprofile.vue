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
        <v-list-item @click="userSession.session.logout()">{{ gettext('Logout') }}</v-list-item>
      </v-list>
    </v-menu>
  </v-btn>
</template>

<script lang="ts">
// import actionHandlerMixin from 'dynamicforms/src/mixins/actionHandlerMixin';
import { defineComponent } from 'vue';

import { apiClient as ApiClient } from '../../apiClient';
import ProjectBaseData from '../../projectBaseData';

import useUserSessionStore from './state';

const chgPassFakeUUID = 'fake-uuid-chg-pass-654654-634565';
const userProfileFakeUUID = 'fake-uuid-usr-prof-654654-634565';
const impUserFakeUUID = 'fake-uuid-imp-user-654654-634565';

export default defineComponent({
  name: 'UserProfile',
  data() {
    return {
      permissions: {} as any,
      impersonateModalVisible: false as boolean,
      userSession: useUserSessionStore(),
    };
  },
  mounted() {
    this.loadData();
    // eventBus.$on(`tableActionExecuted_${chgPassFakeUUID}`, this.dialogBtnClick);
    // eventBus.$on(`tableActionExecuted_${userProfileFakeUUID}`, this.dialogBtnClick);
    // eventBus.$on(`tableActionExecuted_${impUserFakeUUID}`, this.dialogBtnClick);
  },
  unmounted() {
    // eventBus.$off(`tableActionExecuted_${chgPassFakeUUID}`);
    // eventBus.$off(`tableActionExecuted_${userProfileFakeUUID}`);
    // eventBus.$off(`tableActionExecuted_${impUserFakeUUID}`);
  },
  methods: {
    async loadData(force: boolean = false) {
      new ProjectBaseData().getPermissions((p) => { this.permissions = p; });
      if (this.userSession.loggedIn && !force) return;

      await this.userSession.checkLogin(false);
    },
    showImpersonateLogin() {
      window.dynamicforms.dialog.fromURL('/account/impersonate/new.componentdef', 'new', impUserFakeUUID);
    },
    reloadAfterImpersonationChange() {
      this.loadData(true).finally(() => {
        window.location.href = '/';
      });
    },
    stopImpersonation() {
      ApiClient.post('/account/impersonate/end').then(() => {
        userSession.impersonated = false;
        this.reloadAfterImpersonationChange();
      });
    },
    userProfile() {
      window.dynamicforms.dialog.fromURL(
        `/account/profile/${this.componentData.id}.componentdef`,
        'edit',
        userProfileFakeUUID,
      );
    },
    changePassword() {
      window.dynamicforms.dialog.fromURL('/account/change-password/new.componentdef', 'new', chgPassFakeUUID);
    },
    dialogBtnClick(payload: any) {
      let data;
      let params;
      if (payload.action.name !== 'cancel') {
        if (payload.modal.currentDialog.tableUuid === chgPassFakeUUID) {
          data = {
            old_password: payload.data.old_password,
            password: payload.data.password,
            password_confirm: payload.data.password_confirm,
          };
          params = {
            detailUrl: '/account/change-password/submit-change/',
            headers: undefined,
          };
        } else if (payload.modal.currentDialog.tableUuid === userProfileFakeUUID) {
          data = payload.data;
          params = { detailUrl: `/account/profile/${this.componentData.id}.json` };
        } else if (payload.modal.currentDialog.tableUuid === impUserFakeUUID) {
          data = { id: payload.data.user_id };
          params = {
            detailUrl: '/account/impersonate/start',
            submitMethod: 'post',
            headers: undefined,
            then: (() => {
              this.impersonateModalVisible = false;
              userSession.impersonated = true;
              this.reloadAfterImpersonationChange();
            }),
          };
        }
      }
      // actionHandlerMixin.methods.executeTableAction(payload.action, data, payload.modal, params);
    },
  },
});
</script>
