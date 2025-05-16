import {
  Action,
  ConsumerLogicApi,
  dfModal as dfModalApi,
  dfModal,
  DialogSize,
  DisplayMode,
  FilteredActions,
  FormConsumerOneShotApi,
  FormPayload,
  gettext,
  interpolate,
} from '@velis/dynamicforms';
import { AxiosError } from 'axios';
import _ from 'lodash-es';
import { h, reactive, ref, Ref } from 'vue';

import { apiClient } from '../../api-client';

import useUserSessionStore from './state';
import { showLoginDialog } from './use-login-dialog';

const payload: Ref<FormPayload | null> = ref(null);
const socialAuth = ref([]) as Ref<any[]>;
const pwd = ref();
const formDef = reactive({} as any); // as APIConsumer.FormDefinition
const errors = reactive({} as { [key: string]: any[] });
const resetPasswordErrors = reactive({} as { [key: string]: any[] });

let resetPasswordData = { user_id: 0, timestamp: 0, signature: '' };

function parseErrors(apiErr: AxiosError<any>, errsStore: { [key: string]: any[] }) {
  Object.keys(errsStore).forEach((key: string) => {
    delete errsStore[key];
  });
  if (apiErr.response?.data?.detail) {
    errsStore.non_field_errors = [apiErr.response.data.detail];
  } else {
    Object.assign(errsStore, apiErr.response?.data);
  }
}

function getMessage(firstLogin: boolean) {
  let header;
  let body;
  if (firstLogin) {
    header = gettext('Set password');
    body = gettext(`This is your first login. Verification code was sent to your email. 
Please enter this code and set your password to be able to start using this application.`);
  } else {
    header = gettext('Password recovery');
    body = gettext('If an active account exists with the given email, we\'ve sent a message to it.');
  }
  return [
    h('h2', { class: 'mt-n6 mb-4' }, header),
    h(
      'h4',
      { class: 'd-flex justify-center mb-4' },
      [body],
    ),
    h('div', {}, [
      h(
        'h4',
        { class: 'd-flex justify-center mb-1' },
        [interpolate('%(text)s:', { text: gettext('Please enter the code from the message') })],
      ),
      h('input', {
        type: 'text',
        placeholder: resetPasswordErrors.code ? resetPasswordErrors.code : gettext('Email code'),
        id: 'password-reset-input-code',
        class: 'w-100 mb-2 p-1 rounded border-lightgray',
      }, {}),
      h('h4', { class: 'd-flex justify-center mt-2 mb-1' }, [gettext('Please enter your new password:')]),
      h('input', {
        type: 'password',
        placeholder: resetPasswordErrors.password ? resetPasswordErrors.password : gettext('New password'),
        id: 'password-reset-input',
        class: 'w-100 mb-2 p-1 rounded border-lightgray',
      }, {}),
      h('input', {
        type: 'password',
        placeholder: resetPasswordErrors.password_confirm ? resetPasswordErrors.password_confirm : gettext(
          'Confirm password',
        ),
        id: 'password-reset-input-confirmation',
        class: 'w-100 mb-2 p-1 rounded border-lightgray',
      }, {}),
    ]),
  ];
}

function useLogin() {
  const userSession = useUserSessionStore();
  // Tole je za register formo pomoje - ko gre spremenljivka showLoginDialog na true.
  const loginConsumer = new ConsumerLogicApi(userSession.apiEndpointLogin);

  async function enterResetPasswordData(firstLogin: boolean = false) {
    // eslint-disable-next-line vue/max-len
    if (_.includes(window.location.hash, '#reset-user-password') || _.includes(window.location.hash, '#/reset-user-password')) {
      const resetEmailPromise = await dfModal.message('', () => getMessage(firstLogin), new FilteredActions({
        cancel: new Action({
          name: 'cancel',
          label: gettext('Cancel'),
          displayStyle: { asButton: true, showLabel: true, showIcon: true },
          position: 'FORM_FOOTER',
        }),
        confirm: new Action({
          name: 'reset',
          label: firstLogin ? gettext('Confirm') : gettext('Reset'),
          displayStyle: { asButton: true, showLabel: true, showIcon: true },
          position: 'FORM_FOOTER',
        }),
      }));
      if (resetEmailPromise.action.name === 'reset') {
        const password: String | null = (<HTMLInputElement>document.getElementById('password-reset-input')).value;
        const passwordConfirmation: String | null = (<HTMLInputElement>document.getElementById(
          'password-reset-input-confirmation',
        )).value;
        apiClient.post('/account/reset-password/', {
          user_id: resetPasswordData.user_id,
          timestamp: resetPasswordData.timestamp,
          signature: resetPasswordData.signature,
          password,
          password_confirm: passwordConfirmation,
          code: (<HTMLInputElement>document.getElementById('password-reset-input-code')).value,
        }).then(() => {
          window.location.hash = '';
          userSession.checkLogin(false).then(() => {
            if (firstLogin) {
              dfModal.message('', gettext('Password was set successfully'));
            } else {
              dfModal.message('', gettext('Password was reset successfully'));
            }
          });
        }).catch((err: any) => {
          parseErrors(err, resetPasswordErrors);
          enterResetPasswordData(firstLogin);
        });
        return;
      }
      window.location.hash = '';
    }
  }

  async function actionResetPassword() {
    showLoginDialog.value = false;
    const resetEmailPromise = await dfModal.message('', () => [
      h('h2', { class: 'mt-n6 mb-4' }, gettext('Password recovery')),
      h('h4', { class: 'd-flex justify-center mb-1' }, gettext('Enter your e-mail')),
      h('input', {
        type: 'text',
        id: 'input-reset-email',
        class: 'w-100 mb-2 p-1 rounded border-lightgray',
      }, {}),
    ], new FilteredActions({
      cancel: new Action({
        name: 'cancel',
        label: gettext('Cancel'),
        displayStyle: { asButton: true, showLabel: true, showIcon: true },
        position: 'FORM_FOOTER',
      }),
      confirm: new Action({
        name: 'confirm',
        label: gettext('Confirm'),
        displayStyle: { asButton: true, showLabel: true, showIcon: true },
        position: 'FORM_FOOTER',
      }),
    }));
    if (resetEmailPromise.action.name === 'confirm') {
      const email: String | null = (<HTMLInputElement>document.getElementById('input-reset-email')).value;
      apiClient.post('/account/send-reset-password-link/', { email }).then((res: any) => {
        resetPasswordData = res.data;
        window.location.hash = '#reset-user-password';
        enterResetPasswordData();
      });
    }
  }

  async function resetUserState() {
    const modalMessageReset = await dfModalApi.message(
      gettext('Account reactivation'),
      () => [
        h(
          'h5',
          {},
          // eslint-disable-next-line vue/max-len
          gettext('Your account will be restored. Do you want to keep all your previous data or do you want to reset account state and begin as account was just registered and your previous data is deleted?'),
        ),
      ],
      new FilteredActions({
        confirm: new Action({
          name: 'confirm',
          label: gettext('Reset account'),
          displayStyle: { asButton: true, showLabel: true, showIcon: true },
          position: 'FORM_FOOTER',
        }),
        cancel: new Action({
          name: 'cancel',
          label: gettext('Cancel'),
          displayStyle: { asButton: true, showLabel: true, showIcon: true },
          position: 'FORM_FOOTER',
        }),
      }),
      { size: DialogSize.SMALL },
    );
    const resetUserPayload = { reset: false };
    if (modalMessageReset.action.name === 'confirm') {
      resetUserPayload.reset = true;
    }
    await apiClient.post('/account/profile/reset-user-data', payload).then(() => {
      window.location.reload();
    });
  }

  async function doLogin() {
    if (payload.value?.login || payload.value?.password) {
      const result = await userSession.login(payload.value?.login, payload.value?.password);
      if (result?.status === 200) {
        // Tukaj notri sploh ne pride. Zato, ker se že prej naredi reload.
        // nothing to do: login was a success
        if (userSession.deleteAt) {
          await resetUserState();
        }
        return;
      }
      if (result?.response?.status === 400) {
        parseErrors(result, errors);
      } else if (result?.response?.status === 403 && result?.response?.data?.detail === 'new_user') {
        apiClient.post('/account/send-reset-password-link/', {
          username: payload.value?.login,
          firstLogin: true,
        }).then((res: any) => {
          resetPasswordData = res.data;
          window.location.hash = '#reset-user-password';
          enterResetPasswordData(true);
        });
        return;
      } else {
        Object.keys(errors).forEach((key: string) => {
          delete errors[key];
        });
        errors.non_field_errors = [gettext('Unknown error trying to login')];
      }
    }
    showLoginDialog.value = true;
  }

  async function getFormDefinition() {
    await userSession.checkLogin(false);
    _.assignIn(formDef, await loginConsumer.getFormDefinition());
    payload.value = formDef.payload;
    formDef.layout.fields.social_auth_providers.setVisibility(DisplayMode.SUPPRESS);
    formDef.actions.actions.cancel.actionCancel = () => {
      showLoginDialog.value = false;
    };
    formDef.actions.actions.submit.actionSubmit = () => {
      doLogin();
      showLoginDialog.value = false;
    };
    socialAuth.value = formDef.payload.social_auth_providers;
  }

  const openRegistration = async () => FormConsumerOneShotApi(
    { url: '/account/profile/register', trailingSlash: false },
  );

  const newAccount = async () => {
    showLoginDialog.value = false;
    await openRegistration();
  };

  return {
    errors,
    formDef,
    payload,
    pwd,
    socialAuth,
    actionResetPassword,
    doLogin,
    getFormDefinition,
    newAccount,
    openRegistration,
  };
}

export { useLogin, parseErrors };
