import { Session } from '../session';

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
      };
    },
    created() {
    },
    mounted() {
      Session.checkLogin(false);
    },
    computed: {},
    methods: {
      makeLogin() {
        Session.login(this.loginModel.username, this.loginModel.password);
      },
    },
  },
};

// eslint-disable-next-line import/prefer-default-export
export { login };
