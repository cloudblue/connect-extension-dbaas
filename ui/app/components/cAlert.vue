<!-- cAlert Component

  Usage:

  c-alert(
    message="This is alert",    // Alert text, also can be inserted to "message" slot
    :icon="icons.googleStarBaseline",                // Sets icon name
    dense,                      // Makes it dense
    fluid,                      // Makes it fluid
    type="warning",             // Sets alert color to one of following
                                // styles: info, error, success, warning
  )
    template(#message="")
      strong Lorem #[i] Ipsum   // Inserts html to message slot

    c-button(#actions="") Ok    // Inserts content to actions slot

-->

<template lang="pug">
.c-alert-holder
  .c-alert(:class="classSettings",)
    .c-alert__icon
      c-icon(:icon="icon")
    .c-alert__text
      slot(name="message") {{ message }}
    .c-alert__actions(v-if="this.$slots.actions",)
      slot(name="actions")
</template>

<script>
import {
  googleInfoBaseline,
} from '@cloudblueconnect/material-svg/baseline';

import {
  flip,
  includes,
  is,
} from 'ramda';


import cIcon from '~components/cIcon.vue';


import {
  pathTo,
} from '~utils';


const typeAlert = [
  'info',
  'error',
  'success',
  'warning',
  'default',
];

export default {
  components: {
    cIcon,
  },

  props: {
    message: {
      type: String,
      default: 'List is empty. Please add item.',
    },

    icon: {
      type: Object,
      default: () => (googleInfoBaseline),
    },

    dense: {
      type: Boolean,
    },

    alignTop: {
      type: Boolean,
    },

    fluid: {
      type: Boolean,
    },

    type: {
      type: String,
      validator: flip(includes)(typeAlert),
      default: 'default',
    },
  },

  computed: {
    isStringIcon: pathTo(['icon'], is(String)),
    classSettings() {
      return {
        'c-alert_align-top': this.alignTop,
        'c-alert_fluid': this.fluid,
        'c-alert_dense': this.dense,
        [`c-alert_${this.type}`]: true,
      };
    },
  },
};
</script>

<style lang="stylus">
@import '~styles/common';

.c-alert {
  display: inline-flex;
  align-items: center;

  min-height: $module * 16;
  min-width: 240px;
  max-width: 600px;
  padding: $module * 4;
  border-radius: 2px;

  background-color: rgba($mid-grey, 0.15);

  box-sizing: border-box;

  color: $mid-grey;

  &__icon {
    flex: 0 0 auto;
    margin-right: $module * 3;
    display: flex;

    > .c-icon,
    > .v-icon {
      color: currentColor;
    }
  }
  &__text {
    flex: 1 1 auto;
    font-size: $theme-font-size-smaller px;
    line-height: $module * 5;
    text-align: left;
    color: $base-text-color;
  }
  &__text:first-letter{
    text-transform: uppercase;
  }
  &__actions {
    flex: 0 0 auto;
    margin-right: -($module);
    margin-left: $module * 6;

    button {
      margin: -($module / 2) 0;

      & + & {
        margin-left: $module * 4;
      }
    }
  }

  &_align-top{
    align-items: flex-start;
  }
  &_align-top &__icon {
    margin-top: -2px;
  }

  &_dense {
    min-height: $module * 14;
    padding-top: $module * 3;
    padding-bottom: $module * 3
  }
  &_dense &__actions {
    margin-right: -($module * 2);

    button {
      margin-top: -($module);
      margin-bottom: -($module);
    }
  }
  &_fluid {
    display: flex;
    max-width: none;
  }

  &_error {
    background-color: rgba($nice-red, 0.2);
    color: $nice-red;
  }
  &_info {
    background-color: _rgba($accent-rgb, 0.15);
    color: $accent;
  }
  &_success {
    background-color: rgba($green, 0.15);
    color: $green;
  }
  &_warning {
    background-color: rgba($nice-yellow, 0.15);
    color: $nice-yellow;
  }
}
</style>
