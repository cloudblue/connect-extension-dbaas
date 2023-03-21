<template lang="pug">
.status-mark
  c-icon.status-mark__icon(
    :icon="localStatus.icon",
    :style="{color: localStatus.color}",
    :size="16",
  )
  span.status-mark__text(
    v-if="showText",
    locator="status-value",
  )
    span.capitalize(:key="localStatus.text")
      | {{ localStatus.text || '' | replaceUnderscoreToSpaces }}
</template>


<script>
import {
  mergeDeepRight,
  propOr,
  replace,
} from 'ramda';


import cIcon from '~components/cIcon.vue';


import {
  statuses,
} from '~constants';


export default {
  components: {
    cIcon,
  },

  props: {
    status: {
      type: String,
      required: true,
    },

    custom: {
      type: Object,
      default: () => ({}),
    },

    showText: {
      type: Boolean,
      default: true,
    },
  },

  computed: {
    localStatus: vm => mergeDeepRight(
      propOr({}, vm.status, statuses),
      vm.custom,
    ),
  },

  filters: {
    replaceUnderscoreToSpaces: replace(/_/g, ' '),
  },
};
</script>


<style lang="stylus">
@import '~styles/common';

.status-mark {
  display: inline-flex;
  align-items: center;
  vertical-align: middle;

  &__icon {
    margin-right: 4px;
    flex: 0 0 auto;
  }

  &__text {
    color: $base-text-color;
    font-size: 14px;
    line-height: 20px;
    white-space: nowrap;
  }
}
</style>
