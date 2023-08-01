import { ref } from 'vue';

export const showLoginDialog = ref<boolean>(false);

export default function useLoginDialog() {
  const openLoginDialog = () => {
    showLoginDialog.value = true;
  };

  const closeLoginDialog = () => {
    showLoginDialog.value = false;
  };

  return { openLoginDialog, closeLoginDialog };
}
