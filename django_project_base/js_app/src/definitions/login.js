import {Session} from '../session';

const login = {
  id: 'login',
  definition: {
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
  }
};

export {login};