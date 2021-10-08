<template>
  <div style="position: relative">
    <slot name="form-error"><div v-if="getErrorText"><small :id="'form-' + uuid + '-err'"
                                   class="form-text text-danger">{{ getErrorText }}</small><hr></div></slot>
    <input type="text" @keyup="searchUsers"
           v-model="
/* eslint-disable */
record['user']"
           class="autocomplete form-control"
           id="userAutocomplete"
           data-toggle="dropdown" v-bind:placeholder="searchUserPlaceholder"/>
    <ul class="dropdown-menu" style="width: 100%" role="menu">
      <li style="width: 100%; padding: 0 .75rem" @click="selectUser(user)" v-for="(user, idx) in usersFilter"
          v-bind:key="'key_' + user.id + '_' + idx" class="cursor-pointer"><a>{{
          user.full_name || user.email
        }}</a></li>
    </ul>
  </div>
</template>

<script>
// eslint-disable-next-line import/no-extraneous-dependencies
import eventBus from 'dynamicforms/src/logic/eventBus';
import _ from 'lodash';

import { apiClient as ApiClient } from '../../apiClient';

export default {
  name: 'accounts-impersonate_dialog.html',
  props: ['rows', 'uuid', 'record'],
  data() {
    return {
      usersFilter: [],
      errors: {},
    };
  },
  mounted() {
    eventBus.$on(`formEvents_${this.uuid}`, (payload) => {
      if (payload.type === 'submitErrors') {
        this.errors = payload.data;
      }
    });
  },
  beforeDestroy() {
    eventBus.$off(`formEvents_${this.uuid}`);
  },
  computed: {
    searchUserPlaceholder() {
      return this.gettext('Enter any user attribute');
    },
    userSearchInputQueryString() {
      return this.record.user;
    },
    getErrorText() {
      try {
        let errors = '';
        // eslint-disable-next-line no-unused-vars
        _.forIn(this.errors, (value, key) => {
          errors += `${value}\n`;
        });
        errors = errors.trim();
        return errors;
        // eslint-disable-next-line no-empty
      } catch (e) {}
      return '';
    },
  },
  methods: {
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
    selectUser(user) {
      // TODO: Ali je tole spodnje v redu, da se kar spreminja... Trenutno drugače ne znam.
      //  Se pa že itak spreminja, če je vezano na v-model...

      // eslint-disable-next-line vue/no-mutating-props
      this.record.user_id = user.id;
      // eslint-disable-next-line vue/no-mutating-props
      this.record.user = user.full_name || user.email;
    },
  },
};
</script>
