<template lang="pug">
.fancy-icon(
  :style="containerStyles",
)
  .fancy-icon__notification(
    v-if="hasNotification",
  )
  c-icon(
    :icon="icon",
    :size="preparedIconSize",
  )
</template>

<script>
import {
  always,
  either,
  lte,
  max,
  mergeAll,
  pipe,
  prop,
} from 'ramda';


import cIcon from '~components/cIcon.vue';


import {
  hexToStyleVar,
} from '~helpers';

import {
  pathIfElse,
  pathTo,
  propsTo,
} from '~utils';


export const getIconSize = pipe(
  max(16),
  v => v - (v - 16) / 2,
);


export default {
  components: {
    cIcon,
  },

  props: {
    color: {
      type: String,
      required: false,
    },

    icon: {
      type: Object,
      required: true,
    },

    hasNotification: {
      type: Boolean,
      default: false,
    },

    size: {
      type: Number,
      default: 32,
      validator: lte(16),
    },

    iconSize: {
      type: Number,
    },
  },

  computed: {
    componentColor: pathIfElse(['color'], hexToStyleVar('theme_accent_rgb'), always(null)),
    containerSize: pathTo(['size'], size => ({ width: `${size}px`, height: `${size}px` })),
    containerStyles: propsTo(['containerSize', 'componentColor'], mergeAll),
    preparedIconSize: either(
      prop('iconSize'),
      pathTo(['size'], getIconSize),
    ),
  },
};
</script>

<style lang="stylus">
@import '~styles/common.styl';

.fancy-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex: 0 0 auto;
  border-radius: 50%;
  background-color: _rgba($accent-rgb, 0.2);

  &__notification {
    min-width: 12px;
    height: 12px;
    position: absolute;
    top: 0;
    right: 0;
    border-radius: 50%;
    background-color: $red;
  }

  .c-icon {
    color: _rgb($accent-rgb);
  }
}

</style>
