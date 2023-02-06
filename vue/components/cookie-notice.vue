<template>
  <div/>
</template>
<script>
// eslint-disable-next-line import/extensions
import 'vanilla-cookieconsent/src/cookieconsent.js';
import _ from 'lodash';

export default {
  name: 'CookieNotice',
  props: {
    options: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  mounted() {
    try {
      const cookieConsent = window.initCookieConsent();
      cookieConsent.run(_.size(this.options) > 0 ? this.options : (this.$root.$data || {}));
    } catch (error) {
      console.error('Invalid options for cookie notice.');
    }
  },
};
</script>

<style scoped>
  @import '~vanilla-cookieconsent/dist/cookieconsent.css';
</style>
