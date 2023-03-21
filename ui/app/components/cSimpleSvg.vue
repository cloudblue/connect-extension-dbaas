<template lang="pug">
svg(
  :class="classes",
  xmlns="http://www.w3.org/2000/svg",
  :width="width || size",
  :height="height || size",
  :viewBox="`0 0 ${viewBox} ${viewBox}`",
  @click="$emit('click', $event)",
)
  slot
    path(d="M0 0h24v24H0z" fill="none")
    path(:style="{ fill: realColor }" :d="correctPath")
</template>

<script>
import icons from '~tools/icons.json';

import {
  baseTextColor,
} from '~constants';

import {
  pathOrPath,
  template,
} from '~utils';

// TODO: for all such places there will be a theme shared with spa
const colors = {
  primary: '#1565c0',
  accent: '#4797f2',
  contrast: '#ffffff',
};

export default {
  props: {
    path: String,

    size: {
      type: String,
      default: '24',
    },

    width: String,
    height: String,

    viewBox: {
      type: String,
      default: '24',
    },

    color: {
      type: String,
      default: baseTextColor,
    },
  },

  computed: {
    correctPath: ({ path }) => icons[`${path}_icon`] || path,

    classes: template({
      'c-icon_disabled': ['disabled'],
      'c-icon_link': pathOrPath(['$listeners', 'click'], ['$listeners', '!click']),
    }),

    realColor: ({ color }) => colors[color] || color,
  },
};
</script>

<style lang="stylus">
@import '~styles/variables';

.c-icon {
  color: #757575;
  caret-color: currentColor;

  vertical-align: text-bottom;
  fill: currentColor;

  height: 24px;
  width: 24px;

  &_disabled {
    pointer-events: none;
    color: #c5c5c5 !important;
  }

  &_link {
    cursor: pointer;
    outline: none;
  }

  button & {
           color: inherit;
         }
}
</style>
