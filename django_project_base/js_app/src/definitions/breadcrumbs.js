import _ from 'lodash';

const breadcrumbs = {
  id: 'breadcrumbs',
  definition: {
    data() {
      return {};
    },
    created() {

    },
    mounted() {

    },
    computed: {
      currentBreadcrumbsLocation() {
        let data = window.location.pathname;
        //todo: remove
        data = '/peoject/ddd/info/last.html';
        let parts = _.filter(_.trim(data, '/').split('/'), l => l);
        return _.map(parts,
          v => {
            let _idx = _.indexOf(parts, v);
            let _url = _.take(parts, _idx + 1);
            return {
              'url': '/' + _.join(_url, '/'),
              'breadcrumb': _.startCase(
                _.replace(_.replace(v, '.html', ''), ' ', ''))
            };
          }
        );
        //return brd;
        // return _.concat({
        //   'url': '/',
        //   'breadcrumb': 'Home'
        // }, brd);
      },
    },
    methods: {},
  }
};

export {breadcrumbs};