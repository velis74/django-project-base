import Vue from 'vue';

Vue.component('titlebar-extended', {
  extends: '',
  mixins: [],
  data() {
    return {checked: false, title: 'Check me extended'};
  },
  methods: {
    check() {
      console.log(Math.random() + 'extended');
      this.checked = !this.checked;
    }
  }
});

let TitleBarExtended = null;

if (document.getElementById('django-project-base-titlebar-extended')) {
  TitleBarExtended = new Vue({
    el: '#django-project-base-titlebar-extended'
  });
}

export default {TitleBarExtended};