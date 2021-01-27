import Vue from 'vue';

Vue.component('project-list', {
  mixins: [projectListMixin], // jshint ignore:line
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

let ProjectList = null;

if (document.getElementById('django-project-base-project-list')) {
  ProjectList = new Vue({
    el: '#django-project-base-project-list',
  });
}

export default {ProjectList};