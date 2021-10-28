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
            <div v-html="item.text"/>
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

<script>
// https://www.npmjs.com/package/vue-notification is the library used for notification
import Vue from 'vue';
import Notifications from 'vue-notification';

Vue.use(Notifications);
export default {
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
};
</script>

<style scoped>

</style>
