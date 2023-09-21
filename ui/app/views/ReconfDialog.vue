<template lang="pug">
ez-dialog(
  v-model="dialogOpened",
  width="580",
  title="Request Reconfiguration",
  :error-text="errorText",
)
  .detail-item
    .detail-item-head.item-label._mb_12 Type
    .detail-item__text.type-radiogroup
      input#regen(type="radio" v-model="form.subject" value="regenerate_access", materialize)
      label(for="regen", materialize) Regenerate Access Information
      input#change(type="radio" v-model="form.subject" value="change_sizing", materialize)
      label(for="change", materialize) Change Sizing
      input#drop(type="radio" v-model="form.subject" value="drop_db", materialize)
      label(for="drop", materialize) No longer need this database
      input#other(type="radio" v-model="form.subject" value="other", materialize)
      label(for="other", materialize) Other

  .detail-item
    .detail-item-head.item-label._mb_8 Please Describe Details Of Your Request
    .detail-item__text
      textarea(v-model="form.description", materialize)

  template(#actions="")
    c-button(
      mode="outlined",
      label="Cancel",
      @click="close",
    )

    c-button(
      :disabled="!isFormValid",
      :loading="saving",
      mode="solid",
      label="Request Reconfiguration",
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


const SUBJECTS = {
  regenerate_access: {
    action: 'update',
    details: 'Regenerate access',
  },
  change_sizing: {
    action: 'update',
    details: 'Change sizing',
  },
  other: {
    action: 'update',
    details: 'Custom',
  },
  drop_db: {
    action: 'delete',
    details: '',
  },
};

const initialForm = () => ({
  subject: '',
  description: '',
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
    acceptTermsAndConds: false,
    form: initialForm(),
    saving: false,
  }),

  computed: {
    isFormValid: ({ form }) => form.subject && (form.subject !== 'other' || form.description.length > 1),
  },

  methods: {
    ...mapActions('bus', ['emit']),

    close() {
      this.dialogOpened = false;
      this.form = initialForm();
      this.$emit('closed');
    },

    async save() {
      this.saving = true;
      const { action, details } = SUBJECTS[this.form.subject];

      try {
        const item = await databases.reconfigure(this.item.id, {
          action,
          details: `${details}\n\n${this.form.description}`,
        });

        this.$emit('saved', item);
        this.close();
      } catch (e) {
        this.errorText = e.message;
        this.emit({ name: 'snackbar:error', value: e });
        /* eslint-disable no-console */
        console.error(e);
      }

      this.saving = false;
    },
  },

  watch: {
    value: {
      immediate: true,
      handler(v) {
        this.errorText = null;
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

<style lang="stylus" scoped>
  .type-radiogroup {
    display: grid;
    grid-row-gap: 12px;
    grid-column-gap: 8px;
    align-items: center;
    grid-template-columns: min-content 1fr;
  }
</style>
