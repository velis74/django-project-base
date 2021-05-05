/* eslint-disable import/prefer-default-export */
/* eslint-disable function-paren-newline */
/* eslint-disable arrow-parens */
/* eslint-disable no-underscore-dangle */
/* eslint-disable prefer-template */
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
        let data = window.location.pathname;
        // todo: remove
        data = '/peoject/ddd/info/last.html';
        const parts = _.filter(_.trim(data, '/').split('/'), l => l);
        return _.map(parts,
          v => {
            const _idx = _.indexOf(parts, v);
            const _url = _.take(parts, _idx + 1);
            return {
              url: '/' + _.join(_url, '/'),
              breadcrumb: _.startCase(
                _.replace(_.replace(v, '.html', ''), ' ', '')),
            };
          },
        );
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

export { breadcrumbs };
