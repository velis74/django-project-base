<template>
  <div>
    <p>
      {{
        gettext(
          `Please sign in with one of your existing third party accounts. Or, sign up for a ${appname}
        account and sign in below:`,
        )
      }}
    </p>
    <div class="text-center my-6">
      <a v-for="(b, bidx) in socialAuth" :key="bidx" :href="b.url" :aria-label="b.title">
        <social-logos :social-provider="b.name" :title="b.title"/>
      </a>
    </div>
    <p class="text-center my-2">{{ gettext('or') }}</p>
    <v-divider/>
    <v-container>
      <v-row>
        <v-col>
          <v-text-field
            v-model="payload['username']"
            :label="gettext('Username')"
            :placeholder="gettext('Username')"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-text-field
            ref="pwd"
            v-model="payload['password']"
            :label="gettext('Password')"
            type="password"
            :placeholder="gettext('Password')"
          />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { FormPayload } from 'dynamicforms';
import { Ref, ref } from 'vue';

import { apiClient as ApiClient } from '../../apiClient';

import SocialLogos from './social-logos.vue';

interface Props {
  payload: FormPayload,
  title: Ref<string>,
}

defineProps<Props>();

const socialAuth = ref();
ApiClient.get('/account/social-auth-providers/').then((socialAuthProvidersResponse) => {
  socialAuth.value = socialAuthProvidersResponse.data as any[];
});

// TODO: needs to be moved to /rest/about or to some configuration. definitely needs to be app-specific
const appname = 'Demo app';
</script>

<style scoped>
</style>
