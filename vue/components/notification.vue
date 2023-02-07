<template>
  <notifications :width="width" :position="position">
    <template slot="body" slot-scope="{ item, close }">
      <div
        class="vue-notification"
        :class="item.type"
        @click="item.data.onNotificationClose(item, close, true)"
      >
        <div>
          <div style="display: inline-block; max-width: 95%;" class="notification-title">
            <div v-html="item.title"/>
          </div>
          <div style="display: inline-block; max-width: 95%;" class="notification-content">
            <div style="margin-left: 0.4em;" v-html="item.text"/>
          </div>
          <div
            v-if="item.data.duration === -1"
            style="display: inline-block; float: right; vertical-align: middle;"
          >
            <button class="close" @click="item.data.onNotificationClose(item, close)">
              <i class="fas fa-times fa-xs"/>
            </button>
          </div>
        </div>
      </div>
    </template>
  </notifications>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

// https://www.npmjs.com/package/vue-notification is the library used for notification
export default defineComponent({
  // eslint-disable-next-line vue/multi-word-component-names
  name: 'Notification',
  props: {
    width: {
      type: Number,
      default: 350,
    },
    position: {
      type: String,
      default: 'top center',
    },
  },
});
</script>
