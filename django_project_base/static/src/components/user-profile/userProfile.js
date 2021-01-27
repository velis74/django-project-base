import Vue from 'vue';

Vue.component('user-profile', {
  mixins: [userProfileMixin], // jshint ignore:line
  data() {
    return {};
  },
  created() {

  },
  mounted() {

  },
  computed: {},
  methods: {},
});

let UserProfile = null;

if (document.getElementById('django-project-base-user-profile')) {
  UserProfile = new Vue({
    el: '#django-project-base-user-profile',
  });
}

export default {UserProfile};