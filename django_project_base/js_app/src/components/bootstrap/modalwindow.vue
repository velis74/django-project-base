<template>
  <transition name="modal" v-cloak>
    <div class="modal-mask">
      <div class="modal-wrapper">
        <div class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header">
              <slot name="modal-title">
                <h5 class="modal-title">Modal title</h5>
              </slot>
              <slot name="header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
              </slot>
            </div>
            <div class="modal-body">
              <slot name="body">
                default body
              </slot>
            </div>
            <div class="modal-footer">
              <slot name="footer">
                <button type="button" class="btn btn-secondary">{{ gettext('Close') }}
                </button>
                <button type="button" class="btn btn-primary">{{ gettext('Save changes') }}</button>
              </slot>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'modalwindow',
};
</script>

<style scoped>
  .modal-mask {
      position: fixed;
      z-index: 9999;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, .5);
      display: table;
      transition: opacity .3s ease;
  }

  .modal-wrapper {
      display: table-cell;
      vertical-align: middle;
  }
</style>
