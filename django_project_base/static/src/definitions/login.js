import {Session} from '../session';
import {translationData} from '../translations';

const loginComponentDefinition = {
  defaultId: 'login',
  definition: {
    mixins: [typeof loginMixin === 'undefined' ? {} : loginMixin], // jshint ignore:line
    data() {
      return {
        loginModel: {
          username: null,
          password: null,
        },
        translations: {},
      };
    },
    created() {
      this.translations = translationData;
    },
    mounted() {
    },
    computed: {},
    methods: {
      makeLogin() {
        Session.login(this.loginModel.username, this.loginModel.password);
      },
    },
  }
};

export {loginComponentDefinition};