<script setup lang="ts">
import {
  Action,
  APIConsumer,
  ComponentDisplay,
  ConsumerLogicApi,
  FormConsumerApiOneShot, FormPayload, gettext,
  useActionHandler,
} from '@velis/dynamicforms';
// import _ from 'lodash';
// @ts-ignore
// eslint-disable-next-line import/no-extraneous-dependencies
// import SmsCounter from 'sms-counter';
// eslint-disable-next-line import/no-extraneous-dependencies
// import { stripHtml } from 'string-strip-html';
import { onMounted, onUnmounted, ref } from 'vue';

import { apiClient } from '../apiClient';
import {
  closeNotification,
  showNotification,
} from '../notifications';

const notificationLogic = ref(new ConsumerLogicApi('notification', true));

notificationLogic.value.getFullDefinition();

const actionViewLicense = async (): Promise<boolean> => {
  await FormConsumerApiOneShot('notification-license', true, 'new');
  return true;
};

const actionAddNotification = async (): Promise<boolean> => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const valueChangedHandler = (action: Action, payload: FormPayload) => false;
  // let smsCounter = SmsCounter.count('');
  // payload.number_sms_consumed = smsCounter.messages;
  // payload.number_char_remaining = smsCounter.remaining;
  // if (_.includes(payload.send_on_channels, 'SMS')) {
  //   smsCounter = SmsCounter.count(stripHtml(payload.message_body).result);
  //   payload.number_sms_consumed = smsCounter.messages;
  //   payload.number_char_remaining = smsCounter.remaining;
  // }
  // false;
  await FormConsumerApiOneShot(
    'notification',
    true,
    'new',
    undefined,
    { value_changed: valueChangedHandler },
  );
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
    apiClient.get('notification-license/new/?format=json&decorate-max-price=1').then((licenseResponse) => {
      if (licenseResponse.data.remaining_credit < licenseResponse.data.max_notification_price) {
        showLicenseConsumed();
        return;
      }
      closeNotification(notificationId.value);
    });
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
