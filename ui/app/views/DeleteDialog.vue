<template lang="pug">
ez-dialog(
  v-model="dialogOpened",
  width="580",
  title="Delete database",
)
  span Are you sure?

  template(#actions="")
    c-button(
      mode="outlined",
      label="Cancel",
      @click="close",
    )

    c-button(
      mode="solid",
      :loading="saving",
      label="Delete",
      color="accent",
      @click="save",
    )
</template>

<script>
import {
  mapActions,
} from 'vuex';


import ezDialog from '~components/ezDialog.vue';
import cButton from '~components/cButton.vue';

import databases from '~api/databases';


export default {
  components: {
    ezDialog,
    cButton,
  },

  props: {
    value: Boolean,
    item: [Object, null],
  },

  data: () => ({
    dialogOpened: false,
    saving: false,
  }),

  methods: {
    ...mapActions('bus', ['emit']),

    close() {
      this.dialogOpened = false;
      this.$emit('closed');
    },

    async save() {
      this.saving = true;

      try {
        await databases.delete(this.item.id);

        this.$emit('saved');
        this.close();
      } catch (e) {
        this.emit({ name: 'snackbar:error', value: e });
      }

      this.saving = false;
    },
  },

  watch: {
    value: {
      immediate: true,
      handler(v) {
        this.dialogOpened = v;
      },
    },

    dialogOpened(v) {
      if (this.value !== v) this.$emit('input', v);
    },
  },
};
</script>

<style lang="stylus">
@import '~styles/common';
</style>
