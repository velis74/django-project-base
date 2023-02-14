<template>
  <div style="position: relative">
    <slot name="form-error">
      <div v-if="getErrorText">
        <small :id="'form-' + uuid + '-err'" class="form-text text-danger">{{ getErrorText }}</small>
        <hr>
      </div>
    </slot>
    <input
      id="userAutocomplete"
      v-model="record.user"
      type="text"
      class="autocomplete form-control"
      data-toggle="dropdown"
      :placeholder="searchUserPlaceholder"
      @keyup="searchUsers"
    >
    <ul class="dropdown-menu" style="width: 100%" role="menu">
      <li
        v-for="(user, idx) in usersFilter"
        :key="'key_' + user.id + '_' + idx"
        style="width: 100%; padding: 0 .75rem"
        class="cursor-pointer"
        @click="selectUser(user)"
      >
        <a>{{ user.full_name || user.email }}</a>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
// TODO: rewrite DF eventbus
// eslint-disable-next-line import/no-extraneous-dependencies
// import eventBus from 'dynamicforms/src/logic/eventBus';
import _ from 'lodash';
import { defineComponent } from 'vue';

import { apiClient as ApiClient } from '../../apiClient';

export default defineComponent({
  name: 'accounts-impersonate-dialog.html', // eslint-disable-line vue/component-definition-name-casing
  props: {
    uuid: { type: String, required: true },
    record: { type: Object, required: true },
  },
  data() {
    return {
      usersFilter: [] as any[],
      errors: {} as Object,
    };
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
        _.forIn(this.errors, (value) => {
          errors += `${value}\n`;
        });
        errors = errors.trim();
        return errors;
        // eslint-disable-next-line no-empty
      } catch (e) {}
      return '';
    },
  },
  mounted() {
    // eventBus.$on(`formEvents_${this.uuid}`, (payload) => {
    //   if (payload.type === 'submitErrors') {
    //     this.errors = payload.data;
    //   }
    // });
  },
  beforeDestroy() {
    // eventBus.$off(`formEvents_${this.uuid}`);
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
    selectUser(user: any) {
      // TODO: Ali je tole spodnje v redu, da se kar spreminja... Trenutno drugače ne znam.
      //  Se pa že itak spreminja, če je vezano na v-model...

      // eslint-disable-next-line vue/no-mutating-props
      this.record.user_id = user.id;
      // eslint-disable-next-line vue/no-mutating-props
      this.record.user = user.full_name || user.email;
    },
  },
});
</script>
