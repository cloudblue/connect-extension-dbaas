<template lang="pug">
c-simple-dialog(
  v-model="dialogOpened",
  width="800",
  title="Request Reconfiguration",
)
  c-card(title="Type")
    .two-columns
      .choice-card(
        :class="{ 'choice-card__chosen': form.subject === 'regenerate_access' }",
        @click="form.subject = 'regenerate_access'",
      )
        input#access(type="radio" v-model="form.subject" value="regenerate_access", materialize)
        label._ml_8(for="regenerate_access", materialize) Regenerate Access Information

      .choice-card(
        :class="{ 'choice-card__chosen': form.subject === 'change_sizing' }",
        @click="form.subject = 'change_sizing'",
      )
        input#sizing(type="radio" v-model="form.subject" value="change_sizing", materialize)
        label._ml_8(for="change_sizing", materialize) Change Sizing

      .choice-card(
        :class="{ 'choice-card__chosen': form.subject === 'drop_db' }",
        @click="form.subject = 'drop_db'",
      )
        input#drop._ml_24(type="radio" v-model="form.subject" value="drop_db", materialize)
        label._ml_8(for="drop_db", materialize) No longer need this database

      .choice-card(
        :class="{ 'choice-card__chosen': form.subject === 'other' }",
        @click="form.subject = 'other'",
      )
        input#other._ml_24(type="radio" v-model="form.subject" value="other", materialize)
        label._ml_8(for="other", materialize) Other

  ._mt_24

  c-card(title="Additional Information")
    .detail-item
      .detail-item-head.item-label._mb_8 Please describe details of your request
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

import cSimpleDialog from '~components/cSimpleDialog.vue';
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
    cSimpleDialog,
    cButton,
  },

  props: {
    value: Boolean,
    item: [Object, null],
  },

  data: () => ({
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
@import "~styles/common"

.choice-card {
  display: flex;
  padding: 24px;
  box-sizing: border-box;
  align-items: center;
  background-color: $white-smoke;
  border-radius: 2px;
  margin-bottom: 16px;
  cursor: pointer;

  &__chosen {
    background-color: _rgba($accent-rgb, .15);
    outline: 1px solid $accent;
  }
}
</style>
