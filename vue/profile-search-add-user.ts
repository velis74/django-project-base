import { Action, dfModal, DialogSize, FilteredActions, gettext } from '@velis/dynamicforms';
import { h } from 'vue';

// @ts-ignore
import ProfileSearch from './components/profile-search.vue';
import { UserDataJSON } from './components/user-session/data-types';

let selectedUser: UserDataJSON | undefined;

// todo: https://taiga.velis.si/project/velis74-dynamic-forms/us/836?no-milestone=1
function selected(profile: UserDataJSON) {
  selectedUser = profile;
}

async function showAddProfileModal(addCallback: (profile: UserDataJSON | undefined) => any, searchUrl: string) {
  const modal = await dfModal.message(
    gettext('Add new user'),
    () => [h('div', [h(
      // @ts-ignore
      ProfileSearch,
      // @ts-ignore
      { onSelected: selected, searchUrl },
    ), h('div', { style: 'padding-bottom: 4em;' })]),
    ],
    new FilteredActions({
      cancel: new Action({
        name: 'cancel',
        label: gettext('Cancel'),
        displayStyle: { asButton: true, showLabel: true, showIcon: true },
        position: 'FORM_FOOTER',
      }),
      confirm: new Action({
        name: 'add',
        label: gettext('Add'),
        displayStyle: { asButton: true, showLabel: true, showIcon: true },
        position: 'FORM_FOOTER',
      }),
    }),
    { size: DialogSize.LARGE },
  );

  if (modal.action.name === 'add') {
    if (selectedUser) {
      addCallback(selectedUser);
      return;
    }
    await dfModal.message('', gettext('No user selected'));
  }
}

export default showAddProfileModal;
