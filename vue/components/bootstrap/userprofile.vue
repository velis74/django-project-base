<template>
  <ul class="navbar-nav">
    <li class="nav-item dropdown userprofile-component">
      <a
        id="navbarDropdown"
        class="nav-link dropdown-toggle text-nowrap"
        href="#"
        role="button"
        data-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="false"
      >
        <img v-if="componentData.avatar" :src="componentData.avatar" class="d-inline-block align-top size-2">
        <h5 v-if="displayName" class="d-inline-block">
          {{ displayName }}
          <span v-if="isImpersonated">({{ gettext('Impersonated') }})</span>
        </h5>
      </a>
      <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdown">
        <a class="dropdown-item" href="#" @click="userProfile">{{ gettext('User profile') }}</a>
        <a class="dropdown-item" href="#" @click="changePassword">{{ gettext('Change password') }}</a>
        <a
          v-if="permissions['impersonate-user'] && !isImpersonated"
          class="dropdown-item"
          href="#"
          @click="showImpersonateLogin"
        >{{ gettext('Impersonate user') }}</a>
        <a
          v-else-if="isImpersonated"
          class="dropdown-item"
          href="#"
          @click="stopImpersonation"
        >{{ gettext('Stop impersonation') }}</a>
        <div class="dropdown-divider"/>
        <a class="dropdown-item" href="#" @click="makeLogout">{{ gettext('Logout') }}</a>
      </div>
    </li>
  </ul>
</template>

<script>

import 'bootstrap';
// eslint-disable-next-line import/no-extraneous-dependencies
// import eventBus from 'dynamicforms/src/logic/eventBus';
// eslint-disable-next-line import/no-extraneous-dependencies
// import actionHandlerMixin from 'dynamicforms/src/mixins/actionHandlerMixin';
import $ from 'jquery';

import { apiClient as ApiClient } from '../../apiClient';
import ProjectBaseData from '../../projectBaseData';
import { Session } from '../../session';
import { Store } from '../../store';

const chgPassFakeUUID = 'fake-uuid-chg-pass-654654-634565';
const userProfileFakeUUID = 'fake-uuid-usr-prof-654654-634565';
const impUserFakeUUID = 'fake-uuid-imp-user-654654-634565';

export default {
  name: 'UserProfile',
  data() {
    return {
      componentData: {},
      permissions: {},
      isImpersonated: false,
    };
  },
  computed: {
    displayName() {
      if (this.componentData.first_name && this.componentData.last_name) {
        return `${this.componentData.first_name} ${this.componentData.last_name}`;
      }
      if (this.componentData.email) return this.componentData.email;
      if (this.componentData.username) return this.componentData.username;
      return null;
    },
  },
  created() {
    this.loadData();
  },
  mounted() {
    // eventBus.$on(`tableActionExecuted_${chgPassFakeUUID}`, this.dialogBtnClick);
    // eventBus.$on(`tableActionExecuted_${userProfileFakeUUID}`, this.dialogBtnClick);
    // eventBus.$on(`tableActionExecuted_${impUserFakeUUID}`, this.dialogBtnClick);
  },
  updated() {
    // We have to do this otherwise dropdown does not work https://stackoverflow.com/a/29006010/1760858
    this.$nextTick(() => { $('.dropdown-toggle').dropdown(); });
  },
  beforeDestroy() {
    // eventBus.$off(`tableActionExecuted_${chgPassFakeUUID}`);
    // eventBus.$off(`tableActionExecuted_${userProfileFakeUUID}`);
    // eventBus.$off(`tableActionExecuted_${impUserFakeUUID}`);
  },
  methods: {
    loadData(force = false) {
      new ProjectBaseData().getPermissions((p) => {
        this.permissions = p;
      });
      this.isImpersonated = !!Store.get('impersonated-user');
      const cachedProfile = Store.get('current-user');
      if (cachedProfile && !force) {
        this.componentData = cachedProfile;
        return;
      }
      // eslint-disable-next-line consistent-return
      return new Promise((resolve, reject) => {
        ApiClient.get('/account/profile/current').then((profileResponse) => {
          this.componentData = profileResponse.data;
          Store.set('current-user', this.componentData);
          resolve();
        }).catch((err) => {
          reject(err);
        });
      });
    },
    makeLogout() {
      Session.logout();
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
        Store.delete('impersonated-user');
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
    dialogBtnClick(payload) {
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
              Store.set('impersonated-user', true);
              this.reloadAfterImpersonationChange();
            }),
          };
        }
      }
      // actionHandlerMixin.methods.executeTableAction(payload.action, data, payload.modal, params);
    },
  },
};
</script>

<style scoped>
  .cursor-pointer {
    cursor: pointer;
  }

  .card-body {
    padding: 0;
  }

  .card {
    background-color: transparent !important;
    border: none;
  }

  .card-title {
    margin-bottom: 0;
  }
</style>
