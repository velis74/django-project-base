<script setup lang="ts">
import { DfApp } from '@velis/dynamicforms';

import LoginDialog from './components/user-session/login-dialog.vue';
</script>

<template>
  <df-app>
    <LoginDialog/>
    <slot/>
  </df-app>
</template>
