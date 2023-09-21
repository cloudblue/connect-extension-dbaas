<template lang="pug">
ez-dialog(
  v-model="dialogOpened",
  width="580",
  title="Request database",
  :error-text="errorText",
)
  // CREATE MODE
  div(v-if="!isEdit")
    .detail-item._mt_0
      .detail-item-head.item-label._mb_8 Name
        sup.red._ml_4 *
      .detail-item__text
        input(required, v-model="form.name", type="text", materialize)

    .detail-item
      .detail-item-head.item-label._mb_8 Region
        sup.red._ml_4 *
      .detail-item__text
        select(required, materialize, v-model="form.region.id")
          option(disabled) Choose region
          option(
            v-for="region in regions",
            :value="region.id",
            :key="region.id",
          ) {{ region.name }}

    .detail-item
      .detail-item-head.item-label._mb_12 Workload Type
      .detail-item__text.vertical-middle
        input#small(type="radio" v-model="form.workload" value="small", materialize)
        label._ml_8(for="small", materialize) Small
        ._ml_24
        input#medium(type="radio" v-model="form.workload" value="medium", materialize)
        label._ml_8(for="medium", materialize) Medium
        ._ml_24
        input#large._ml_24(type="radio" v-model="form.workload" value="large", materialize)
        label._ml_8(for="large", materialize) Large

    p._mt_16._mb_0.assistive-text {{ workloadDescriptions[form.workload] }}
      a._ml_4(
        href="https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-limits#maximum-connections",
        target="_blank",
      ) Read more

  // EDIT MODE
  .detail-item._mt_0(v-if="isEdit")
    .detail-item-head.item-label._mb_8 Name
      sup.red._ml_4 *
    .detail-item__text
      input(required, v-model="form.name", type="text", materialize)

  .detail-item
    .detail-item-head.item-label._mb_8 Technical Contact
      sup._ml_4.red *
    .detail-item__text
      select(
        materialize,
        v-model="form.tech_contact.id",
        :disabled="isEdit && installationContext.isAdmin"
      )
        option(disabled) Choose user
        option(
          v-for="user in (isEdit && installationContext.isAdmin ? [item.tech_contact] : users)",
          :value="user.id",
          :key="user.id",
        ) {{ user.name }} ({{ user.email }})

  .detail-item
    .detail-item-head.item-label._mb_8 Planned Database Workload
      sup.red._ml_4 *
    .detail-item__text
      textarea(v-model="form.description", materialize)

  p.font-size_smaller._mt_24(v-if="!isEdit")
    | By checking the “I have read and accepted the agreement” box located on this page,
    | you agree to be bound by this agreement. You represent and warrant that you have
    | the authority to bind the entity on behalf of which you are creating an account to the
    | terms of this agreement.

  .vertical-middle._mt_16(v-if="!isEdit")
    input#acceptTermsAndConds(
      required,
      type="checkbox"
      v-model="acceptTermsAndConds",
      materialize,
    )

    label._ml_8(required, for="acceptTermsAndConds", materialize)
      | I agree to all terms and conditions

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
      :label="isEdit ? 'Save' : 'Send to review'",
      color="accent",
      @click="save",
    )
</template>

<script>
import {
  clone,
  pick,
} from 'ramda';

import {
  mapActions,
  mapGetters,
} from 'vuex';

import {
  propTo,
  template,
} from '~utils';

import ezDialog from '~components/ezDialog.vue';
import cButton from '~components/cButton.vue';

import databases from '~api/databases';
import regions from '~api/regions';
import context from '~api/context';
import accountUsers from '~api/account-users';


export const initialForm = () => ({
  name: '',
  description: '',
  workload: 'small',
  tech_contact: { id: null },
  region: { id: null },
});

const prepareForm = (isEdit, v) => template({
  name: ['name'],
  description: ['description'],
  tech_contact: propTo('tech_contact', pick(['id'])),
  ...(isEdit ? {} : {
    workload: ['workload'],
    region: propTo('region', pick(['id'])),
  }),
})(v);

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
    saving: false,
    regions: [],
    users: [],
    form: initialForm(),
  }),

  computed: {
    ...mapGetters(['installationContext']),

    isEdit: ({ item }) => Boolean(item),
    allowSaving: ({ isEdit, acceptTermsAndConds, form }) => Boolean((
      isEdit
      && form.name
      && form.description
      && form.workload
      && form.tech_contact.id
    ) || (
      !isEdit
      && acceptTermsAndConds
      && form.name
      && form.description
      && form.region.id
      && form.workload
      && form.tech_contact.id
    )),

    workloadDescriptions: () => ({
      small: 'Plan "B2s". vCores: 2; Mem Size: 4Gb; Max Conns: 100; Max User Conns: 97',
      medium: 'Plan "D2s_v3". vCores: 2; Mem Size: 8Gb; Max Conns: 859; Max User Conns: 856',
      large: 'Plan "D8s_v3". vCores: 8; Mem Size: 32Gb; Max Conns: 3438; Max User Conns: 3435',
    }),
  },

  methods: {
    ...mapActions('bus', ['emit']),

    close() {
      this.dialogOpened = false;
      this.$emit('closed');
      this.form = initialForm();
      this.users = [];
      this.regions = [];
    },

    async save() {
      this.errorText = null;
      this.saving = true;

      try {
        if (this.isEdit) await databases.update(this.item.id, prepareForm(this.isEdit, this.form));
        else await databases.create(prepareForm(this.isEdit, this.form));

        this.$emit('saved');
        this.close();
      } catch (e) {
        this.errorText = e.message;
        this.emit({ name: 'snackbar:error', value: e });
      }

      this.saving = false;
    },
  },

  watch: {
    value: {
      immediate: true,
      async handler(v) {
        if (v) {
          this.errorText = null;
          if (this.item) this.form = clone(this.item);

          try {
            this.regions = await regions.list();
            const { account } = await context.get();
            this.users = await accountUsers.list(account.id);
          } catch (e) {
            /* eslint-disable no-console */
            console.log(e);
          }
        }

        this.dialogOpened = v;
      },
    },

    dialogOpened(v) {
      if (!v) this.form = initialForm();
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
