<!-- Empty Screen Placeholder component
  Usage:
  empty-screen-placeholder(
    :icon="vpnKey",                      // Object - Places icon
    color="#BDBDBD",                      // HEX - "#BDBDBD" - sets icon color
    title="Title",                        // String - Places title

    @action="add",                 // Function - button action. Required to display
    :button-visible="showBtn",            // Boolean - true - configures button visibility
    button-text="Add Item",               // String - "Add one" - configures button label

    alert-text="Lorem ipsum",             // String - alert text. Required to display alert
    :alert-visible="showAlert",           // Boolean - true - configures alert visibility

    @alert-action="add",           // Function - alert button action. Required to display
    :alert-button-visible="showBtn",      // Boolean - true - configures alert button visibility
    alert-button-text="Add Item",         // String - "Add one" - configures alert button label
  )
    span Some content                     // Slot - places placeholder text
-->
<template lang="pug">
.screen-placeholder(:class="{'screen-placeholder_fullsize': fullsize}")
  .screen-placeholder__content
    c-fancy-icon.screen-placeholder__icon(
      v-if="icon",
      :icon="icon",
      :color="color",
      :size="96",
    )

    h2.screen-placeholder__header(locator="screen-placeholder_header") {{ title }}

    p.screen-placeholder__text(v-show="$slots.default")
      slot

    c-alert.screen-placeholder__alert(
      v-if="alertVisible && !!alertText",
      locator="alert-state-placeholder",
      :message="alertText",
    )
      template(#actions="")
        c-button(
          v-if="alertButtonVisible && !!alertButtonText",
          color="accent",
          @click="alertAction",
          locator="screen-placeholder_alert-button",
          :label="alertButtonText",
        )

    .screen-placeholder__actions(
      v-if="buttonVisible && !!buttonText",
    )
      c-button.screen-placeholder__button(
        :disabled="buttonDisabled",
        mode="outlined",
        color="accent",
        locator="screen-placeholder_action-button",
        @click="action",
        :label="buttonText",
      )
        template(#icon="")
          ez-svg(path="add", color="accent")
</template>

<script>
import cAlert from '~components/cAlert.vue';
import cButton from '~components/cButton.vue';
import cFancyIcon from '~components/cFancyIcon.vue';

import ezSvg from '~components/ezSvg.vue';


export default {
  components: {
    cFancyIcon,
    cAlert,
    cButton,
    ezSvg,
  },

  props: {
    icon: Object,

    color: {
      type: String,
      default: '#BDBDBD',
    },

    title: {
      type: String,
      default: '',
    },

    buttonText: String,

    buttonVisible: {
      type: Boolean,
      default: true,
    },

    alertText: String,
    alertVisible: {
      type: Boolean,
      default: true,
    },

    alertButtonVisible: {
      type: Boolean,
      default: true,
    },

    alertButtonText: String,
    fullsize: Boolean,
    buttonDisabled: Boolean,
    entityName: String,
  },

  methods: {
    action() {
      this.$emit('action');
    },

    alertAction() {
      this.$emit('alert-action');
    },
  },
};
</script>

<style lang="stylus">
@import '~styles/common.styl';

$sz-regular = 24px;
$sz-medium = 32px;
$sz-large = 40px;

$offset = 20vh;
$max-width = 600px;

$light-grey = #e0e0e0;

.screen-placeholder {
  position: relative;
  margin: auto;
  flex: 0 0 auto;

  &_fullsize {
    position: absolute;
    left: 0;
    top: 170px;
    right: 0;
    bottom: 0;
    z-index: 1;
    display: flex;
    background-color: #fff;

    &::before {
      content: '';
      position: absolute;
      top: -100px;
      left: 0;
      width: 100%;
      height: 100px;
      background: linear-gradient(to top, #FFFFFF, rgba(255, 255, 255, 0));
    }
  }

  &__content {
    max-width: $max-width;
    padding-bottom: $offset;
    flex: 0 0 auto;
    margin: auto;
  }

  &__icon {
    margin-left: auto;
    margin-right: auto;
  }

  &__header {
    margin-top: $sz-medium;
    margin-bottom: 0;
    font-size: $theme-font-size-h1 px;
  }

  &__text {
    margin-top: $sz-regular;
    margin-bottom: 0;
    font-size: $theme-font-size px;
  }

  &__text,
  &__header {
    color: $theme-black-5;
    line-height: $theme-line-height-h2 px;
  }
  &__text,
  &__header,
  &__actions {
    text-align: center;
  }

  &__alert {
    margin-top: $sz-large;
    margin-bottom: 0;
    text-align: center;
  }

  &__actions {
    margin-top: $sz-large;
  }

  &__button {
    margin: 0;
    border-color: $light-grey !important;
  }
}
</style>
