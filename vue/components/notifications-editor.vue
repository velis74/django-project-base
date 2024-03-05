<script setup lang="ts">
import {
  APIConsumer,
  ComponentDisplay,
  ConsumerLogicApi, FormConsumerOneShotApi, gettext,
  useActionHandler,
} from '@velis/dynamicforms';
import { onMounted, onUnmounted, ref } from 'vue';

import { apiClient } from '../api-client';
import {
  closeNotification,
  showNotification,
} from '../notifications';

const props = defineProps<{
  consumerUrl?: string,
  consumerUrlTrailingSlash?: boolean,
  licenseConsumerUrl?: string,
  licenseConsumerUrlTrailingSlash?: boolean,
}>();

const consumerUrl: string = (props.consumerUrl ?? 'notification') as string;
const consumerTrailingSlash = (props.consumerUrlTrailingSlash ?? true) as boolean;

const licenseConsumerUrl = (props.licenseConsumerUrl ?? 'notification-license') as string;
const licenseConsumerUrlTrailingSlash = (props.licenseConsumerUrlTrailingSlash ?? true) as boolean;

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
    useQueryInRetrieveOnly: true,
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

handler
  .register('view-license', actionViewLicense)
  .register('add-notification', actionAddNotification);

const handlers = {
  edit: async (action: any, payload: any) => {
    console.log('K1');
    await FormConsumerOneShotApi({
      url: consumerUrl,
      trailingSlash: licenseConsumerUrlTrailingSlash,
      pk: payload.id,
    });
    return true;
  },
};
</script>

<template>
  <!--suppress TypeScriptValidateTypes -->
  <!-- @vue-ignore -->
  <APIConsumer
    :consumer="notificationLogic"
    :handlers="handlers"
    :display-component="ComponentDisplay.TABLE"
  />
</template>
