const modalWindow = {
  id: 'modal-window',
  type: 'x-template',
  definition: {
    template: `#modal-window`,
    data() {
      return {};
    },
    created() {
    },
    mounted() {

    },
    computed: {},
    methods: {
      open() {
        console.log('open');
      },
      close() {
        console.log('close');
      },
    },
  },
};

export {modalWindow};
