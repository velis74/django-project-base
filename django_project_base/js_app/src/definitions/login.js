/* eslint-disable import/prefer-default-export */
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
    },
    computed: {},
    methods: {
      makeLogin() {
        Session.login(this.loginModel.username, this.loginModel.password);
      },
    },
  },
};

export { login };
