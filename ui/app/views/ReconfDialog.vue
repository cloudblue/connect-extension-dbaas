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
      .detail-item-head.item-label._mb_8 Please describe details of your request (optional)
      .detail-item__text
        textarea(v-model="form.description", materialize)

  template(#actions="")
    c-button(
      mode="outlined",
      label="Cancel",
      @click="close",
    )

    c-button(
      :disabled="!form.subject",
      mode="solid",
      label="Request Reconfiguration",
      color="accent",
      @click="save",
    )
</template>

<script>
import {
  clone,
} from 'ramda';

import cSimpleDialog from '~components/cSimpleDialog.vue';
import cButton from '~components/cButton.vue';

import databases from '~api/databases';


const SUBJECTS = {
  regenerate_access: 'Regenerate Access Information for',
  change_sizing: 'Change sizing of',
  drop_db: 'Delete',
  other: 'Perform some action on',
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
    mode: {
      type: String,
      default: 'create',
    },
  },

  data: () => ({
    dialogOpened: false,
    acceptTermsAndConds: false,
    form: initialForm(),
  }),

  methods: {
    close() {
      this.dialogOpened = false;
      this.form = initialForm();
      this.$emit('closed');
    },

    async save() {
      const item = await databases.reconfigure(this.item.id, {
        case: {
          ...this.form,

          subject: `${SUBJECTS[this.form.subject]} ${this.item.id}`,
        },
      });
      this.$emit('saved', item);
      this.close();
    },
  },

  watch: {
    value: {
      immediate: true,
      handler(v) {
        if (v && this.mode !== 'create' && this.item) this.form = clone(this.item);
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
