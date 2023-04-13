<template lang="pug">
ez-dialog(
  v-model="dialogOpened",
  width="800",
  title="Activate database",
  :error-text="errorText",
)
  ui-card(title="Access")
    .detail-item._mt_0
      .detail-item-head.item-label._mb_8 Username
        sup.red._ml_4 *
      .detail-item__text
        input(required, v-model="form.credentials.username", type="text", materialize)

    .detail-item
      .detail-item-head.item-label._mb_8 Password
        sup.red._ml_4 *
      .detail-item__text
        input(required, v-model="form.credentials.password", type="password" materialize)

    .detail-item
      .detail-item-head.item-label._mb_8 Host
        sup.red._ml_4 *
      .detail-item__text
        input(required, v-model="form.credentials.host", type="text", materialize)

    .detail-item
      .detail-item-head.item-label._mb_8 DB Name
      .detail-item__text
        input(v-model="form.credentials.name", type="text", materialize)

  ._mt_24

  ui-card(title="General")
    .detail-item._mt_0
      .detail-item-head.item-label._mb_12 Workload type
      .detail-item__text.vertical-middle
        input#small(type="radio" v-model="form.workload" value="small", materialize)
        label._ml_8(for="small", materialize) Small
        ._ml_24
        input#medium(type="radio" v-model="form.workload" value="medium", materialize)
        label._ml_8(for="medium", materialize) Medium
        ._ml_24
        input#large._ml_24(type="radio" v-model="form.workload" value="large", materialize)
        label._ml_8(for="large", materialize) Large

  template(#actions="")
    c-button(
      mode="outlined",
      label="Cancel",
      @click="close",
    )

    c-button(
      :disabled="!allowSaving",
      mode="solid",
      :loading="saving",
      label="Activate",
      color="accent",
      @click="save",
    )
</template>

<script>
import {
  clone,
} from 'ramda';

import {
  mapActions,
} from 'vuex';

import {
  template,
} from '~utils';

import ezDialog from '~components/ezDialog.vue';
import cButton from '~components/cButton.vue';

import databases from '~api/databases';



const initialForm = () => ({
  credentials: {
    name: '',
    host: '',
    username: '',
    password: '',
  },
  workload: 'small',
});

const prepareForm = template({
  workload: ['workload'],
  credentials: ['credentials'],
});

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
    errorText: null,
    dialogOpened: false,
    saving: false,
    form: initialForm(),
  }),

  computed: {
    allowSaving: ({ form }) => Boolean((
      form.credentials.username
      && form.credentials.password
      && form.credentials.host
    )),
  },

  methods: {
    ...mapActions('bus', ['emit']),

    close() {
      this.dialogOpened = false;
      this.$emit('closed');
      this.form = initialForm();
    },

    async save() {
      this.errorText = null;
      this.saving = true;

      try {
        await databases.activate(this.item.id, prepareForm(this.form));

        this.$emit('saved');
        this.close();
      } catch (e) {
        if (e.status === 422) {
          this.errorText = 'An input error occurred. Please fill all required fields';
        } else {
          this.errorText = `#${e.status} ${e.message}`;
        }

        this.emit({ name: 'snackbar:error', value: e });
      }

      this.saving = false;
    },
  },

  watch: {
    value: {
      immediate: true,
      handler(v) {
        const data = clone(this.item);
        if (!data?.credentials) data.credentials = initialForm().credentials;
        this.form = data;

        this.dialogOpened = v;
      },
    },

    dialogOpened(v) {
      if (!v) {
        this.errorText = null;
        this.form = initialForm();
      }

      if (this.value !== v) this.$emit('input', v);
    },
  },
};
</script>

<style lang="stylus">
@import '~styles/common';
</style>

<style lang="stylus" scoped>
@import '~styles/common';

.red {
  color: $nice-red;
}

.vertical-middle {
  display: flex;
  justify-content: flex-start;
  flex-direction: row;
  align-items: center;
}
</style>
