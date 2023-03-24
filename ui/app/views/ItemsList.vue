<template lang="pug">
div
  ez-toolbar._mb_16
    template(#actions="")
      c-button(
        mode="solid",
        label="Request New Database",
        color="accent",
        @click="openCreationDialog",
      )
        template(#icon="")
          ez-svg(
            path="add",
            color="white",
            size="18",
          )

  c-screen-placeholder(
    v-if="showPlaceholder",
    :icon="placeholderIcon",
    title="No databases",
    @action="openCreationDialog",
    button-text="Request new database",
    fullsize,
  )
    | Request cloud-based database storage through this extension, but please be aware
    | that each request will be subject to review and approval by the CloudBlue team.
    br
    | For more information, please refer to our documentation.

  ez-table(
    v-else,
    v-model="list",
    :loading="loading",
    :columns="columns",
  )
    template(#workload="{ value }")
      span.capitalize {{ value }}

    template(#name="{ item }")
      .detail-item
        a.detail-item__text(@click="$emit('item-clicked', item)") {{ item.name }}
        .detail-item__assistive-text {{ item.id }}

    template(#description="{ value }")
      span.assistive-text {{ value }}

    template(#status="{ value }")
      c-status(:status="value")

  database-dialog(
    v-model="dialogOpened",
    @saved="load",
  )
</template>

<script>
import {
  googleStorageBaseline,
} from '@cloudblueconnect/material-svg/baseline';

import {
  isNilOrEmpty,
} from '~utils';

import databases from '~api/databases';

import cScreenPlaceholder from '~components/cScreenPlaceholder.vue';
import cStatus from '~components/cStatus.vue';
import cButton from '~components/cButton.vue';

import ezTable from '~components/ezTable.vue';
import ezToolbar from '~components/ezToolbar.vue';
import ezSvg from '~components/ezSvg.vue';

import DatabaseDialog from '~views/CreateEditDialog.vue';


export default {
  components: {
    cScreenPlaceholder,
    cStatus,
    cButton,
    ezSvg,
    ezTable,
    ezToolbar,
    DatabaseDialog,
  },

  data: () => ({
    dialogOpened: false,
    loading: false,
    list: [],
  }),

  computed: {
    placeholderIcon: () => googleStorageBaseline,

    showPlaceholder: ({ list, loading }) => !loading && isNilOrEmpty(list),

    columns: () => [
      { name: 'DB', value: 'name' },
      { name: 'Region', value: 'region.name' },
      { name: 'Workload type', value: 'workload' },
      { name: 'Description', value: 'description' },
      { name: 'Status', value: 'status' },
    ],
  },

  methods: {
    openCreationDialog() {
      this.dialogOpened = true;
    },

    async load() {
      this.loading = true;
      this.list = await databases.list();
      this.loading = false;
    },
  },

  async created() {
    await this.load();
  },
};
</script>

<style lang="stylus">
.two-columns {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  flex-wrap: wrap;

  & > * {
    width: calc(50% - 8px);
  }
}

.vertical-middle {
  display: flex;
  justify-content: flex-start;
  flex-direction: row;
  align-items: center;
}
</style>

