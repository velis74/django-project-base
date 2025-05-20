<template>
  <div>
    <multiselect
      id="profile-selection"
      v-model="selected"
      :options="selectOptions"
      :close-on-select="true"
      :clear-on-select="false"
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
        {{ //@ts-ignore
          props.option.email }}
        {{ //@ts-ignore
          props.option.first_name }}
        {{ //@ts-ignore
          props.option.last_name }}
      </template>
    </multiselect>
  </div>
</template>

<script setup lang="ts">
import { apiClient, gettext, interpolate } from '@velis/dynamicforms';
import { computed, ref, Ref } from 'vue';
// eslint-disable-next-line import/no-extraneous-dependencies
import Multiselect from 'vue-multiselect';

import { PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME, UserDataJSON } from './user-session/data-types';

const inputProps = defineProps<{
  searchUrl: string,
}>();

const emit = defineEmits(['selected']);

// todo: https://taiga.velis.si/project/velis74-dynamic-forms/us/836?no-milestone=1

const searchUrl: string = (inputProps.searchUrl !== undefined ? inputProps.searchUrl : '/account/profile') as string;

const selected: Ref<UserDataJSON | null> = ref(null);

const searching = ref(false);

const options: Ref<UserDataJSON[]> = ref([]);

const selectOptions = computed(() => options.value);

function asyncSearch(query: string) {
  searching.value = true;
  apiClient.get(interpolate('%(url)s?search=%(query)s', {
    url: searchUrl,
    query,
  }), { showProgress: false }).then((response: any) => {
    options.value = response.data;
    searching.value = false;
  });
}

function onSelect(newVal: UserDataJSON) {
  selected.value = newVal;
  emit('selected', newVal);
}

function addProfile(newProfile: string) {
  const profile: UserDataJSON = {
    email: newProfile,
    full_name: '',
    username: '',
    avatar: '',
    is_impersonated: false,
    password_invalid: false,
    is_superuser: false,
    permissions: [],
    groups: [],
    delete_at: '',
    [PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME]: '',
  };
  options.value.push(profile);
  selected.value = profile;
  onSelect(profile);
}

function customLabel(profile: UserDataJSON) {
  return interpolate('%(mail)s %(name)s', {
    mail: profile.email ? profile.email : '',
    name: profile.full_name ? profile.full_name : '',
  });
}

</script>
