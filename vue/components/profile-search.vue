<script setup lang="ts">

import { apiClient, gettext } from '@velis/dynamicforms';
import { computed, ref } from 'vue';
// eslint-disable-next-line import/no-extraneous-dependencies
import Multiselect from 'vue-multiselect';

import { PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME } from './user-session/data-types';

const inputProps = defineProps<{
  searchUrl: {
    type: String,
    required: false,
  },
}>();

const emit = defineEmits(['selected']);

const searchUrl: string = (inputProps.searchUrl !== undefined ? inputProps.searchUrl : '/account/profile') as string;

const selected = ref(null);

const searching = ref(false);

const options = ref([]);

const selectOptions = computed(() => options.value);

function asyncSearch(query: string) {
  searching.value = true;
  apiClient.get(`${searchUrl}?search=${query}`).then((response) => {
    options.value = response.data;
    searching.value = false;
    console.log(options.value);
  });
}

function addProfile(newProfile) {
  console.log(newProfile);
  const profile = { email: newProfile };
  profile[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME] = null;
  options.value.push(profile);
  selected.value = profile;
}

function onSelect(newVal) {
  selected.value = newVal;
  console.log('emitting vall ....');
  emit('selected', newVal);
}

function customLabel(profile) {
  return `${profile.email ? profile.email : ''}
  ${profile.first_name ? profile.first_name : ''} ${profile.last_name ? profile.last_name : ''}`;
}

</script>

<template>
  <div>
    {{ selected }}

    <multiselect
      id="profile-selection"
      v-model="selected"
      :options="selectOptions"
      :close-on-select="true"
      :clear-on-select="true"
      :internal-search="false"
      :hide-selected="false"
      :preserve-search="true"
      :placeholder="gettext('Type to search or enter a new email value')"
      :track-by="PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME"
      :preselect-first="false"
      label="email"
      :custom-label="customLabel"
      :taggable="true"
      :tag-placeholder="gettext('Add this email as new user')"
      @search-change="asyncSearch"
      @tag="addProfile"
      @select="onSelect"
    >
      <template slot="singleLabel" slot-scope="props">
        {{ props.option.email }}
        {{ props.option.first_name }}
        {{ props.option.last_name }}
      </template>
    </multiselect>
  </div>
</template>
