<template>
  <cookie-law :message="message || defaultMessage"/>
</template>
<script>
import translationsMixin from 'dynamicforms/src/mixins/translationsMixin';
import CookieLaw from 'vue-cookie-law';

export default {
  name: 'CookieNotice',
  components: {
    CookieLaw,
  },
  mixins: [translationsMixin],
  props: {
    message: {
      type: String,
      // eslint-disable-next-line max-len
      default: null,
    },
  },
  computed: {
    defaultMessage() {
      // eslint-disable-next-line max-len
      return this.gettext('Our site saves small pieces of text information (cookies) on your device in order to deliver better content and for statistical purposes. You can disable the usage of cookies by changing the settings of your browser. By browsing our website without changing the browser settings you grant us permission to store that information on your device.');
    },
  },
  methods: {},
};
</script>

<style scoped>

</style>
