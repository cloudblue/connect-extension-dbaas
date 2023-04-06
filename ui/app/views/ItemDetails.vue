<template lang="pug">
div
  ez-loader(
    v-if="loading",
    size="70",
    fullscreen,
    move-up="24"
  )

  ez-toolbar(
    v-if="!loading",
    :on-back="onBack",
    :title="localItem.name || ''",
    subtitle="Database Details",
  )
    template(#actions="")
      c-button._mr_16(
        v-if="installationContext.isAdmin",
        mode="solid",
        label="Activate",
        color="accent",
        @click="openActivateDialog",
      )

      c-button._mr_16(
        v-if="installationContext.isAdmin",
        mode="solid",
        label="Delete",
        color="accent",
        @click="openDeleteDialog",
      )

      c-button._mr_16(
        v-if="!installationContext.isAdmin",
        :disabled="localItem.status !== 'active'",
        mode="solid",
        label="Request Reconfiguration",
        color="accent",
        @click="openReconfigureDialog",
      )
        template(#icon="")
          ez-svg(
            path="chat_bubble_outline",
            :color="localItem.status !== 'active' ? '#bdbdbd' : 'white'",
            size="18",
          )

      c-button(
        mode="outlined",
        label="Edit",
        @click="openEditDialog",
      )

  .container(v-if="!loading")
    .two-columns
      ui-card(title="General")
        .item-row
          .item-label ID
          .item-value {{ localItem.id }}

        .item-row
          .item-label Status
          .item-value
            c-status(:status="localItem.status")

        .item-row(
          v-if="localItem.case && ['reviewing', 'reconfiguring'].includes(localItem.status)",
        )
          .item-label Ticket
          a.item-value.capitalize(@click="redirect(localItem.case.id)") {{ localItem.case.id }}

        .item-row
          .item-label Region
          .item-value.capitalize {{ localItem.region.name }}

        .item-row
          .item-label Workload Type
          .item-value.capitalize {{ localItem.workload }}

        .divider._mt_24._mb_24

        .item-row
          .item-label Created
          .item-value {{ localItem.events.created.at | ddmmyyyy }}

        .item-row(v-if="localItem.events.updated")
          .item-label Updated
          .item-value {{ localItem.events.updated.at | ddmmyyyy }}

      ui-card(title="Technical Contact")
        .detail-item
          .detail-item-head.item-label._mb_8 User
          .detail-item__text {{ localItem.tech_contact.name }}
          .detail-item__assistive-text {{ localItem.tech_contact.email }}

        .detail-item
          .detail-item-head.item-label._mb_8 Planned database workload
          .detail-item__text {{ localItem.description }}

    ui-card._mt_24(title="Access information", v-if="localItem && localItem.credentials")
      .item-row
        .item-label URL
        .item-value {{ hidePassword ? databaseUrl.hidePassword : databaseUrl.showPassword }}
          c-icon.pointer._ml_16(
            :icon="hidePassword ? icons.on : icons.off",
            size="18",
            color="black",
            @click="hidePassword = !hidePassword",
          )

          c-icon.pointer._ml_16(
            :icon="icons.copy",
            size="18",
            color="black",
            @click="$copyText(databaseUrl.showPassword)",
          )

      .item-row
        .item-label DB Name
        .item-value {{ localItem.credentials.name || '–' }}

      .item-row
        .item-label Username
        .item-value {{ localItem.credentials.username }}

      .item-row
        .item-label Password
        .item-value {{ hidePassword ? '••••••••••••' : localItem.credentials.password }}
          c-icon.pointer._ml_16(
            :icon="hidePassword ? icons.on : icons.off",
            size="18",
            color="black",
            @click="hidePassword = !hidePassword",
          )

          c-icon.pointer._ml_16(
            :icon="icons.copy",
            size="18",
            color="black",
            @click="$copyText(localItem.credentials.password)",
          )

      .item-row
        .item-label SSL
        .item-value Required

  database-dialog(
    v-model="isDialogOpened",
    mode="edit",
    :item="localItem",
    @saved="load",
  )

  activate-dialog(
    v-model="isActivateDialogOpened",
    :item="localItem",
    @saved="load",
  )

  delete-dialog(
    v-model="isDeleteDialogOpened",
    :item="localItem",
    @saved="onBack",
  )

  reconf-dialog(
    v-model="isReconfDialogOpened",
    :item="localItem",
    @saved="load",
  )
</template>

<script>
import {
  mapActions,
  mapState,
} from 'vuex';

import {
  concat,
  equals,
  length,
  pipe,
  when,
} from 'ramda';

import {
  googleContentCopyBaseline,
  googleVisibilityBaseline,
  googleVisibilityOffBaseline,
} from '@cloudblueconnect/material-svg';

import cStatus from '~components/cStatus.vue';
import cIcon from '~components/cIcon.vue';
import ezLoader from '~components/ezLoader.vue';
import ezToolbar from '~components/ezToolbar.vue';
import cButton from '~components/cButton.vue';
import ezSvg from '~components/ezSvg.vue';

import ActivateDialog from '~views/ActivateDialog.vue';
import DatabaseDialog from '~views/CreateEditDialog.vue';
import DeleteDialog from '~views/DeleteDialog.vue';
import ReconfDialog from '~views/ReconfDialog.vue';

import databases from '~api/databases';


const norm = pipe(
  String,
  when(
    pipe(
      length,
      equals(1),
    ),
    concat('0'),
  ),
);


export default {
  components: {
    cStatus,
    cIcon,
    ezLoader,
    ezToolbar,
    cButton,
    ezSvg,
    ActivateDialog,
    DatabaseDialog,
    DeleteDialog,
    ReconfDialog,
  },

  props: {
    item: {
      type: Object,
      required: true,
    },
  },

  data: () => ({
    isDialogOpened: false,
    isActivateDialogOpened: false,
    isDeleteDialogOpened: false,
    isReconfDialogOpened: false,
    loading: false,
    hidePassword: true,
    editingItem: null,
    localItem: null,

    icons: {
      on: googleVisibilityBaseline,
      off: googleVisibilityOffBaseline,
      copy: googleContentCopyBaseline,
    },
  }),

  computed: {
    ...mapState(['installationContext']),

    databaseUrl: ({ localItem }) => {
      if (!localItem?.credentials) return { showPassword: '–', hidePassword: '–' };

      const username = encodeURIComponent(localItem.credentials.username);
      const password = encodeURIComponent(localItem.credentials.password);
      const host = encodeURIComponent(localItem.credentials.host);
      const name = localItem.credentials.name && encodeURIComponent(localItem.credentials.name);

      return {
        showPassword: `postgres://${username}:${password}@${host}/${name || ''}?sslmode=require`,
        hidePassword: `postgres://${username}:•••••••••••@${host}/${name || ''}?sslmode=require`,
      };
    },
  },

  methods: {
    ...mapActions('bus', ['emit']),

    openActivateDialog() {
      this.isActivateDialogOpened = true;
    },

    openDeleteDialog() {
      this.isDeleteDialogOpened = true;
    },

    openReconfigureDialog() {
      this.isReconfDialogOpened = true;
    },

    openEditDialog() {
      this.isDialogOpened = true;
    },

    async load() {
      this.loading = true;

      try {
        this.localItem = await databases.get(this.item);
      } catch (e) {
        /* eslint-disable no-console */
        console.log(e);
      }

      this.loading = false;
    },

    onBack() {
      this.$emit('closed');
    },

    redirect(id) {
      this.emit({ name: 'redirect', value: id });
    },
  },

  filters: {
    ddmmyyyy: (dateString) => {
      const date = new Date(dateString);
      const dd = norm(date.getUTCDate());
      const mm = norm(date.getUTCMonth() + 1);
      const yyyy = date.getUTCFullYear();

      return `${dd}/${mm}/${yyyy}`;
    },
  },

  created() {
    this.load();
  },
};
</script>

<style lang="stylus">
@import '~styles/common';
</style>

<style lang="stylus" scoped>
@import '~styles/common';

.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 24px;

  & > * {
    width: 960px;
  }
}

.two-columns {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  flex-wrap: wrap;

  & > * {
    width: calc(50% - 12px);
  }
}

.item-row {
  display: grid;
  grid-template-columns: var(--grid-item-first-col, 100px) 1fr;
  grid-column-gap: 12px;
  align-items: start;
}

.item-row + .item-row {
  margin-top: 12px;
}

.item-label {
  font-weight: 500;
  font-size: 14px;
  line-height: 20px;
  color: $base-text-color;
}
</style>
