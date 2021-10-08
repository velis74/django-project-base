<template>
  <div class="nav-item left-spacing userprofile-component">
    <div class="card" data-toggle="dropdown">
      <div class="card-body">
        <img
          v-if="componentData.avatar"
          :src="componentData.avatar"
          class="float-left rounded-circle"
        >
        <div class="user-names" :style="componentData.avatar ? 'padding-left: 55px;' : ''">
          <h5 v-if="componentData.first_name && componentData.last_name" class="card-title">
            {{ componentData.first_name }} <br> {{ componentData.last_name }}
            <span v-if="isImpersonated">({{
              gettext('Impersonated')
            }})</span>
          </h5>
          <h5 v-else-if="componentData.email" class="card-title" style="margin-top: 0.6em;">
            {{ componentData.email }}
            <span v-if="isImpersonated">({{ gettext('Impersonated') }})</span>
          </h5>
          <h5 v-else-if="componentData.username" class="card-title" style="margin-top: 0.6em;">
            {{ componentData.username }}
            <span v-if="isImpersonated">({{ gettext('Impersonated') }})</span>
          </h5>
        </div>
        <ul class="navbar-nav">
          <li class="nav-item dropdown">
            <div class="dropdown-menu" aria-labelledby="navbarDropdown" style="left: -7em;">
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
              <a class="dropdown-item" href="#" @click="makeLogout">{{
                gettext('Logout')
              }}</a>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>

// eslint-disable-next-line import/no-extraneous-dependencies
import eventBus from 'dynamicforms/src/logic/eventBus';
// eslint-disable-next-line import/no-extraneous-dependencies
import actionHandlerMixin from 'dynamicforms/src/mixins/actionHandlerMixin';
import Vue from 'vue';

import { apiClient as ApiClient } from '../../apiClient';
import ProjectBaseData from '../../projectBaseData';
import { Session } from '../../session';
import { Store } from '../../store';

import ImpersonateDialog from './impersonate_dialog.vue';

Vue.component(ImpersonateDialog.name, ImpersonateDialog);

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
  created() {
    this.loadData();
  },
  mounted() {
    eventBus.$on(`tableActionExecuted_${chgPassFakeUUID}`, this.dialogBtnClick);
    eventBus.$on(`tableActionExecuted_${userProfileFakeUUID}`, this.dialogBtnClick);
    eventBus.$on(`tableActionExecuted_${impUserFakeUUID}`, this.dialogBtnClick);
  },
  beforeDestroy() {
    eventBus.$off(`tableActionExecuted_${chgPassFakeUUID}`);
    eventBus.$off(`tableActionExecuted_${userProfileFakeUUID}`);
    eventBus.$off(`tableActionExecuted_${impUserFakeUUID}`);
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
      window.dynamicforms.dialog.fromURL(
        '/account/impersonate/new.componentdef', 'new', impUserFakeUUID,
      );
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
      window.dynamicforms.dialog.fromURL(`/account/profile/${this.componentData.id}.componentdef`, 'edit',
        userProfileFakeUUID);
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
          data = {
            id: payload.data.user_id,
          };
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
      actionHandlerMixin.methods.executeTableAction(payload.action, data, payload.modal, params);
    },
  },
};
</script>

<style scoped>
  .cursor-pointer {
    cursor: pointer;
  }

  .left-spacing {
    margin-left: 1em;
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
