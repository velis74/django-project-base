<script setup lang="ts">
import {
  APIConsumer,
  ComponentDisplay,
  ConsumerLogicApi,
  FormConsumerApi,
  FormConsumerOneShotApi,
  gettext,
  interpolate,
  RowTypes,
  useActionHandler,
} from '@velis/dynamicforms';
import { onMounted, onUnmounted, ref } from 'vue';

import { apiClient } from '../api-client';
import { closeNotification, showNotification } from '../notifications';

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
  const formConsumer = new FormConsumerApi({
    url: consumerUrl,
    trailingSlash: consumerTrailingSlash,
    pk: 'new',
    useQueryInRetrieveOnly: true,
  });
  await formConsumer.getUXDefinition();
  let data: Partial<any> | undefined;
  let error = {};
  let reload;
  do {
    // eslint-disable-next-line no-await-in-loop
    const formResult = await formConsumer.withErrors(error).execute(data);

    const resultAction = formResult.action;
    data = formResult.data;

    error = {};
    reload = false;
    if (resultAction.action.name === 'submit' || resultAction.action.name === 'save-only') {
      try {
        formResult.data.save_only = resultAction.action.name === 'save-only';
        // eslint-disable-next-line no-await-in-loop
        await formConsumer.save();
        reload = true;
      } catch (err: any) {
        error = { ...err?.response?.data };
      }
    }
    // propagate error to the next dialog
  } while (error && Object.keys(error).length);

  if (reload) {
    await notificationLogic.value.reload();
  }

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
      interpolate('%(url)s/new%(trailingSlash)sformat=json&decorate-max-price=1`', {
        url: licenseConsumerUrl,
        trailingSlash: licenseConsumerUrlTrailingSlash ? '/' : '',
      }),
    ).then(
      (licenseResponse: any) => {
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
  edit: async (action: any, payload: any, context: { rowType: RowTypes }) => {
    if (context.rowType !== RowTypes.Data || payload == undefined) return false; // eslint-disable-line eqeqeq
    await FormConsumerOneShotApi({
      url: consumerUrl,
      trailingSlash: consumerTrailingSlash,
      pk: payload.id,
    }, handlers);
    return true;
  },
  send: async (action: any, payload: any, context: any) => {
    apiClient.put(consumerTrailingSlash ? interpolate('%(url)s/', { url: consumerUrl }) : consumerUrl, {
      id: context.dialog.body.props.payload.id,
      send: true,
    }).then(() => {
      // Moram narediti reload...
      // ker tukaj nimam dostopa do notificationLogic.rows, da bi samo zamenjal vrstico, ki je bila updatana.
      notificationLogic.value.reload();
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
