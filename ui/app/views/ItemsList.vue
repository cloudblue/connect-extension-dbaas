<template lang="pug">
div
  ez-toolbar._mb_24
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
    fix-layout,
  )
    template(#workload="{ value }")
      span.capitalize {{ value }}

    template(#name="{ item }")
      .detail-item
        a.detail-item__text(@click="$emit('item-clicked', item)") {{ item.name }}
        .detail-item__assistive-text
          span {{ item.id }}
          span(v-if="installationContext.isAdmin")  • {{ item.owner.id }}

    template(#description="{ value }")
      .assistive-text {{ value }}

    template(#status="{ value }")
      c-status(:status="value")

  database-dialog(
    v-model="dialogOpened",
    @saved="load",
  )
</template>

<script>
import {
  mapState,
} from 'vuex';

import {
  googleStorageBaseline,
} from '@cloudblueconnect/material-svg/baseline';

import {
  isNilOrEmpty,
} from '~utils';

import databases from '~api/databases';

import cScreenPlaceholder from '~components/cScreenPlaceholder.vue';
import ezTable from '~components/ezTable.vue';
import cStatus from '~components/cStatus.vue';
import cButton from '~components/cButton.vue';
import ezToolbar from '~components/ezToolbar.vue';
import ezSvg from '~components/ezSvg.vue';

import DatabaseDialog from '~views/CreateEditDialog.vue';


export default {
  components: {
    DatabaseDialog,
    cScreenPlaceholder,
    ezTable,
    ezToolbar,
    cStatus,
    cButton,
    ezSvg,
  },

  data: () => ({
    dialogOpened: false,
    loading: false,
    list: [],
  }),

  computed: {
    ...mapState(['installationContext']),

    placeholderIcon: () => googleStorageBaseline,

    showPlaceholder: ({ list, loading }) => !loading && isNilOrEmpty(list),

    columns: () => [{
      name: 'DB',
      value: 'name',

      style: {
        width: '300px',
        paddingLeft: '24px',
      },
    }, {
      name: 'Region',
      value: 'region.name',

      style: {
        width: '100px',
      },
    }, {
      name: 'Workload',
      value: 'workload',

      style: {
        width: '100px',
      },
    }, {
      name: 'Description',
      value: 'description',
    }, {
      name: 'Status',
      value: 'status',

      style: {
        width: '120px',
        paddingLeft: '24px',
      },
    }],
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
@import '~styles/common';
</style>

<style lang="stylus" scoped>
@import '~styles/common';

.two-columns {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  flex-wrap: wrap;

  & > * {
    width: calc(50% - 12px);
  }
}

.vertical-middle {
  display: flex;
  justify-content: flex-start;
  flex-direction: row;
  align-items: center;
}
</style>

