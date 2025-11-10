<template>
  <cached-icon
    :class="`social-logo d-inline-block`"
    :style="`width: ${sizeEm}em; height: ${sizeEm}em; margin: 0 ${hSpacing}em`"
    :name="icons[socialProvider]"
  />
</template>

<script setup lang="ts">
import { CachedIcon } from 'vue-cached-icon';

import icons from './icons';

export interface Props {
  socialProvider: 'facebook' | 'google-oauth2' | 'twitter' | 'microsoft-graph' | 'github' | 'gitlab';
  sizeEm?: number,
}

const props = withDefaults(defineProps<Props>(), { sizeEm: 5 });

const hSpacing = props.sizeEm * 0.1;
</script>
