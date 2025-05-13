<template>
  <v-breadcrumbs :items="currentBreadcrumbsLocation"/>
</template>

<script lang="ts">
import _ from 'lodash-es';
import { defineComponent } from 'vue';

export default defineComponent({
  // eslint-disable-next-line vue/multi-word-component-names
  name: 'Breadcrumbs',
  computed: {
    currentBreadcrumbsLocation() {
      const urlParts = _.filter(_.trim(window.location.pathname, '/').split('/'), (l) => l);
      const hashParts = _.filter(_.trim(window.location.hash.replace(/^[#/]+/, ''), '/').split('/'), (l) => l);
      const parts = urlParts.concat(hashParts) as string[];
      return parts.map(
        (v: string) => {
          const idx = _.indexOf(parts, v);
          let href = `/${_.join(_.take(urlParts, idx + 1), '/')}`;
          if (idx >= urlParts.length) {
            href += `#/${_.join(_.take(hashParts, idx - urlParts.length + 1), '/')}`;
          }
          return { href, disabled: false, title: _.startCase(_.replace(_.replace(v, '.html', ''), ' ', '')) };
        },
      );
    },
  },
});
</script>
