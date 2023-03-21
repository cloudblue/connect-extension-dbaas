<template lang="pug">
.app(:style="styleCustomizations")
  item-details(
    v-if="active === 'details' && item",
    :item="item",
    @closed="openList",
  )

  items-list(
    v-else,
    @item-clicked="openDetails",
  )
</template>

<script>
import ItemsList from './views/ItemsList.vue';
import ItemDetails from './views/ItemDetails.vue';

import styleCustomizations from '~mixins/styleCustomizations';


export default {
  mixins: [
    styleCustomizations(),
  ],

  components: {
    ItemsList,
    ItemDetails,
  },

  data() {
    return {
      active: 'list',
      item: null,
    };
  },

  methods: {
    openDetails(item) {
      this.item = item.id;
      this.active = 'details';
    },

    openList() {
      this.active = 'list';
      this.item = null;
    },
  },
};
</script>

<style lang="stylus">
@import '~styles/app.styl';
</style>

