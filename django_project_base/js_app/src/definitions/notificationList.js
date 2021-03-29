const notificationList = {
  id: 'notification-list',
  type: 'x-template',
  definition: {
    template: `#notification-list`,
    data() {
      return {
        visible: false,
        notifications: [],
      };
    },
    created() {

    },
    mounted() {

    },
    computed: {},
    methods: {
      toggleNotifications(e) {
        e.preventDefault();
        e.stopPropagation();
        this.visible = !this.visible;
      }
    },
  }
};

export {notificationList};