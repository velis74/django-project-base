<script setup lang="ts">
import {
  APIConsumer,
  ComponentDisplay,
  ConsumerLogicApi, FormConsumerOneShotApi, gettext,
  useActionHandler,
} from '@velis/dynamicforms';
import { onMounted, onUnmounted, ref } from 'vue';

import { apiClient } from '../apiClient';
import {
  closeNotification,
  showNotification,
} from '../notifications';

const props = defineProps<{
  consumerUrl: {
    type: String,
    required: false,
  },
  consumerUrlTrailingSlash: {
    type: Boolean,
    required: false,
  },
  licenseConsumerUrl: {
    type: String,
    required: false,
  },
  licenseConsumerUrlTrailingSlash:{
    type: Boolean,
    required: false,
  },
}>();

const consumerUrl: string = (props.consumerUrl !== undefined ? props.consumerUrl : 'notification') as string;
const consumerTrailingSlash = (
    props.consumerUrlTrailingSlash !== undefined ? props.consumerUrlTrailingSlash : true) as boolean;

const licenseConsumerUrl = (
    props.licenseConsumerUrl !== undefined ? props.licenseConsumerUrl : 'notification-license') as string;
const licenseConsumerUrlTrailingSlash = (
    props.licenseConsumerUrlTrailingSlash !== undefined ? props.licenseConsumerUrlTrailingSlash : true) as boolean;

const notificationLogic = ref(new ConsumerLogicApi(
  consumerUrl,
  consumerTrailingSlash,
));

notificationLogic.value.getFullDefinition();

const actionViewLicense = async (): Promise<boolean> => {
  await FormConsumerOneShotApi({ url: licenseConsumerUrl, trailingSlash: licenseConsumerUrlTrailingSlash, pk: 'new' });
  return true;
};

const actionAddNotification = async (): Promise<boolean> => {
  await FormConsumerOneShotApi({
    url: consumerUrl,
    trailingSlash: consumerTrailingSlash,
    pk: 'new',
  });
  return true;
};

const licenseConsumedShown = ref(false);
const notificationId = ref(Date.now());

const showLicenseConsumed = () => {
  if (!licenseConsumedShown.value) {
    notificationId.value = Date.now();
    licenseConsumedShown.value = true;
    showNotification(
      gettext('License consumed'),
      gettext('You cannot generate new notifications. Please contact support.'),
      'error',
      -1,
      notificationId.value,
    );
  }
};

let intervalCheckLicense: NodeJS.Timeout | undefined;
onMounted(() => {
  intervalCheckLicense = setInterval(() => {
    apiClient.get(
      `${licenseConsumerUrl}/new${licenseConsumerUrlTrailingSlash ? '/' : ''}?format=json&decorate-max-price=1`,
    ).then(
      (licenseResponse) => {
        if (licenseResponse.data.remaining_credit < licenseResponse.data.max_notification_price) {
          showLicenseConsumed();
          return;
        }
        closeNotification(notificationId.value);
      },
    );
  }, 15000);
});

onUnmounted(() => clearInterval(intervalCheckLicense));

const { handler } = useActionHandler();

handler.register('view-license', actionViewLicense).register('add-notification', actionAddNotification);

// TODO: remove linter ignores below when you know how to
</script>

<template>
  <div class="overflow-y-auto">
    <!--suppress TypeScriptValidateTypes -->
    <!-- @vue-ignore -->
    <APIConsumer :consumer="notificationLogic" :display-component="ComponentDisplay.TABLE"/>
    <ModalView/>
  </div>
</template>
