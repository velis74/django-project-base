import { Action, dfModal, DialogSize, FilteredActions, gettext } from '@velis/dynamicforms';
import { h } from 'vue';

import ProfileSearch from './components/profile-search.vue';
import { UserDataJSON } from './components/user-session/data-types';

let selectedUser: UserDataJSON | undefined;

function selected(profile: UserDataJSON) {
  selectedUser = profile;
}

async function showAddProfileModal(addCallback: (profile: UserDataJSON | undefined) => any) {
  const modal = await dfModal.message(
    gettext('Add new user'),
    () => [h('div', [h(ProfileSearch, { onSelected: selected })])],
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
