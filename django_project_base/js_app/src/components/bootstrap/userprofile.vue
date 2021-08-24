<template>
  <div class="nav-item left-spacing userprofile-component">
    <div class="card" data-toggle="dropdown">
      <div class="card-body">
        <img v-bind:src="componentData.avatar"
             class="float-left rounded-circle">
        <div class="user-names">
          <h5 class="card-title" v-if="componentData.first_name && componentData.last_name">
            {{ componentData.first_name }} <br/> {{ componentData.last_name }}
            <span v-if="isImpersonated">({{
                gettext('Impersonated')
              }})</span></h5>
          <h5 class="card-title" style="margin-top: 0.6em;" v-else-if="componentData.email">
            {{ componentData.email }}
            <span v-if="isImpersonated">({{ gettext('Impersonated') }})</span></h5>
          <h5 class="card-title" style="margin-top: 0.6em;" v-else-if="componentData.username">
            {{ componentData.username }}
            <span v-if="isImpersonated">({{ gettext('Impersonated') }})</span></h5>
        </div>
        <ul class="navbar-nav">
          <li class="nav-item dropdown">
            <div class="dropdown-menu" aria-labelledby="navbarDropdown" style="left: -4em;">
              <a v-if="permissions['impersonate-user'] && !isImpersonated" class="dropdown-item"
                 @click="showImpersonateLogin" href="#">{{ gettext('Impersonate user') }}</a>
              <a v-else-if="isImpersonated" class="dropdown-item"
                 @click="stopImpersonation" href="#">{{ gettext('Stop impersonation') }}</a>
              <a class="dropdown-item" href="#" @click="makeLogout">{{
                  gettext('Logout')
                }}</a>
            </div>
          </li>
        </ul>
      </div>
    </div>
    <modalwindow v-if="impersonateModalVisible">
      <h5 slot="modal-title">{{ gettext('Search for user') }}</h5>
      <h3 slot="header">
        <button @click="showImpersonateLogin" type="button" class="close" data-dismiss="modal"
                aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </h3>
      <div slot="body" v-if="permissions['add-project']" class="col-sm-9">
        <div class="row">
          <input type="text" @keyup="searchUsers" v-model="userSearchInputQueryString"
                 class="autocomplete form-control"
                 id="userAutocomplete"
                 data-toggle="dropdown" v-bind:placeholder="searchUserPlaceholder"/>
          <ul class="dropdown-menu" style="width: 100%;" role="menu">
            <li style="width: 100%" @click="selectUser(user)" v-for="(user, idx) in usersFilter"
                v-bind:key="'key_' + user.id + '_' + idx" class="cursor-pointer"><a>{{
                user.full_name || user.email
              }}</a></li>
          </ul>
        </div>
      </div>
      <div slot="footer">
        <button class="btn-sm btn-primary" @click="changeUser">{{ gettext('OK') }}</button>
      </div>
    </modalwindow>
  </div>
</template>

<script>
import _ from 'lodash';
import ProjectBaseData from '../../projectBaseData';
import { Store } from '../../store';
import { apiClient as ApiClient } from '../../apiClient';
import { Session } from '../../session';
import modalwindow from './modalwindow.vue';

export default {
  name: 'userprofile',
  data() {
    return {
      componentData: {},
      permissions: {},
      impersonateModalVisible: false,
      usersFilter: [],
      selectedUser: null,
      userSearchInputQueryString: '',
      isImpersonated: false,
    };
  },
  created() {
    this.loadData();
  },
  mounted() {

  },
  computed: {
    searchUserPlaceholder() {
      return this.gettext('Enter any user attribute');
    },
  },
  methods: {
    setAvatarImg(profileData) {
      const { avatar } = profileData;
      if (!avatar) {
        // eslint-disable-next-line no-param-reassign
        profileData.avatar = 'https://via.placeholder.com/45';
      }
      return profileData;
    },
    loadData(force = false) {
      new ProjectBaseData().getPermissions((p) => {
        this.permissions = p;
      });
      this.isImpersonated = !!Store.get('impersonated-user');
      const cachedProfile = Store.get('current-user');
      if (cachedProfile && !force) {
        this.componentData = this.setAvatarImg(cachedProfile);
        return;
      }
      // eslint-disable-next-line consistent-return
      return new Promise((resolve, reject) => {
        ApiClient.get('/account/profile/current').then((profileResponse) => {
          this.componentData = this.setAvatarImg(profileResponse.data);
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
      this.userSearchInputQueryString = '';
      this.impersonateModalVisible = !this.impersonateModalVisible;
    },
    changeUser() {
      ApiClient.post('/account/impersonate/start', { id: this.selectedUser.id }).then(() => {
        this.impersonateModalVisible = false;
        Store.set('impersonated-user', true);
        this.reloadAfterImpersonationChange();
      });
    },
    selectUser(user) {
      this.selectedUser = user;
      this.userSearchInputQueryString = user.full_name || user.email;
    },
    // eslint-disable-next-line func-names
    searchUsers: _.debounce(function () {
      if (!this.userSearchInputQueryString) {
        return;
      }
      const url = `/account/profile?search=${this.userSearchInputQueryString}`;
      ApiClient.get(url).then((response) => {
        this.usersFilter = response.data;
      });
    }, 250),
    reloadAfterImpersonationChange() {
      this.loadData(true).then(() => {
        window.location.href = '/';
      });
    },
    stopImpersonation() {
      ApiClient.post('/account/impersonate/end').then(() => {
        Store.delete('impersonated-user');
        this.reloadAfterImpersonationChange();
      });
    },
  },
  components: {
    modalwindow,
  },
};
</script>

<style scoped>
  .cursor-pointer {
      cursor: pointer;
  }

  .user-names {
    padding-left: 55px;
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
