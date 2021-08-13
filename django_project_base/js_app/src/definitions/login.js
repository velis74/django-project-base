import { Session } from '../session';
import { apiClient as ApiClient } from '../apiClient';
import { Store } from '../store';

const login = {
  id: 'login',
  type: 'x-template',
  definition: {
    template: '#login',
    data() {
      return {
        loginModel: {
          username: null,
          password: null,
        },
        socialAuth: [],
      };
    },
    created() {
    },
    mounted() {
      Session.checkLogin(false).then(() => {
        if (!Store.get('current-user')) {
          ApiClient.get('/account/social-auth-providers/').then((socProvResponse) => {
            this.socialAuth = socProvResponse.data;
          });
        }
      });
    },
    computed: {},
    methods: {
      makeLogin() {
        Session.login(this.loginModel.username, this.loginModel.password);
      },
      focusPassword() {
        document.getElementsByName('psw')[0].focus();
      },
    },
  },
};

// eslint-disable-next-line import/prefer-default-export
export { login };
