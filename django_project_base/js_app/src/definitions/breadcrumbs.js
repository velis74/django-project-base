import _ from 'lodash';

const breadcrumbs = {
  id: 'breadcrumbs',
  type: 'x-template',
  definition: {
    template: '#breadcrumbs',
    data() {
      return {};
    },
    created() {

    },
    mounted() {

    },
    computed: {
      currentBreadcrumbsLocation() {
        const data = window.location.pathname;
        const parts = _.filter(_.trim(data, '/').split('/'), (l) => l);
        return _.map(parts,
          (v) => {
            const idx = _.indexOf(parts, v);
            const url = _.take(parts, idx + 1);
            return {
              url: `/${_.join(url, '/')}`,
              breadcrumb: _.startCase(
                _.replace(_.replace(v, '.html', ''), ' ', ''),
              ),
            };
          });
        // return brd;
        // return _.concat({
        //   'url': '/',
        //   'breadcrumb': 'Home'
        // }, brd);
      },
    },
    methods: {},
  },
};

// eslint-disable-next-line import/prefer-default-export
export { breadcrumbs };
