<template>
  <div class="nav-item breadcrumbs-component" v-if="currentBreadcrumbsLocation.length > 0" v-cloak>
    <div class="card">
      <div class="card-body">
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li v-for="(b, bx) in currentBreadcrumbsLocation" :key="bx" class="breadcrumb-item"><a
                v-bind:href="b.url">{{ b.breadcrumb }}</a></li>
          </ol>
        </nav>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';

export default {
  name: 'breadcrumbs',
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
    },
  },
  methods: {},
};
</script>

<style scoped>
  .breadcrumb {
      margin-bottom: 0;
  }
</style>
