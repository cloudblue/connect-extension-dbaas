<template lang="pug">
.c-dialog(
  v-show="value",
  :class="cDialogClasses",
  @keydown.esc="closeHandler",
)
  transition(name="overlay")
    .c-dialog__overlay(
      v-if="value",
      ref="dialog-overview",
      :class="{ 'c-dialog__overlay-invisible': !showOverlay }",
      @click="outsideClickHandler",
    )

  transition(name="window")
    .c-dialog__window.c-window(
      v-if="value",
      :class="dialogBodyClasses",
      :style="{ height, width, minWidth: width }",
      tabindex="-1",
      :locator="locator",
      :id="id",
      ref="c-window",
    )
      .c-window__header
        h2.c-window__title(locator="dialog-title")

          slot(name="title")
            .truncator
              .truncator__truncate.capitalize-first-letter {{ title }}
              .c-window__status.truncator__keep(v-if="status") — {{ status }}

          .header-actions(v-if="$slots['header-actions']")
            slot(name="header-actions")

        .c-window__message
          c-alert(
            v-if="errorText"
            :message="errorText",
            :icon="icons.googleErrorBaseline",
            dense,
            fluid,
            type="error",
            locator="dialog-error",
          )
            template(#message="")
              slot(name="message", :error-text="errorText")

        .c-window__toolbar(v-if="$slots.toolbar")
          slot(name="toolbar")

      c-scroll-box.c-window__content(
        :class="{ 'c-window__content_no-frame': noFrame }",
        @scroll-at-bottom="$emit('scroll-at-bottom')",
        ref="scrollBox",
      )
        slot

      .c-window__actions(
        :class="{ 'c-window__actions_no-divider': hideActionsDivider }",
      )
        slot(name="actions")
          template(v-for="action in preparedActions")
            .horizontal-spacer(
              v-if="action.type === 'spacer'",
              :key="`${action.label}-divider`",
            )

            c-button(
              v-else-if="!action.hidden",
              :key="action.label",
              :locator="action.key",
              :label="action.label",
              :disabled="action.disabled || isActionLoading[action.label]",
              :color="action.color || 'accent'",
              :loading="action.loading || isActionLoading[action.label]",
              :mode="action.mode || 'outlined'",
              @click="() => actionClickHandler(action)",
              v-bind="action.props",
            )
</template>


<script>
import {
  googleErrorBaseline,
} from '@cloudblueconnect/material-svg/baseline';

import {
  always,
  map,
  propOr,
} from 'ramda';

import cAlert from '~components/cAlert.vue';
import cButton from '~components/cButton.vue';
import cScrollBox from '~components/cScrollBox.vue';

import {
  debounce,
  kebabCase,
  pathTo,
  propOrProp,
  template,
} from '~utils';

import {
  baseTextColor,
} from '~constants';


const SHAKING_DURATION_MS = 150;


export default {
  components: {
    cAlert,
    cScrollBox,
    cButton,
  },

  props: {
    value: Boolean,
    id: String,
    locator: String,
    status: String,
    errorText: String,
    noFrame: Boolean,
    hideActionsDivider: Boolean,
    onCancel: Function,
    showOverlay: Boolean,
    preventOutsideClick: Boolean,
    width: { type: String, default: '500px' },
    height: { type: String, default: 'auto' },

    title: {
      type: String,
      required: true,
    },

    actions: {
      type: Array,
      default: always([{
        label: 'Close',
        closeAfterHandle: true,
        color: baseTextColor,
      }]),
    },
  },

  data() {
    return {
      isActionLoading: {},
      isShaking: false,

      icons: {
        googleErrorBaseline,
      },
    };
  },

  computed: {
    isErrorShown: pathTo(['errorText'], Boolean),
    cDialogClasses: template({ 'c-dialog_opened': ['localValue'] }),
    dialogBodyClasses: template({ 'c-dialog__window_z-shaking': ['isShaking'] }),

    preparedActions: pathTo(['actions'], map(action => ({
      key: `${kebabCase(action.label || '')}-action`,
      ...action,
    }))),

    closeHandler: propOrProp('onCancel', 'closeDialog'),
  },

  methods: {
    async actionClickHandler(action) {
      try {
        if (typeof action.handler === 'function') {
          this.isActionLoading[action.label] = true;
          await action.handler();
        }

        if (action.closeAfterHandle) this.closeDialog();
      } catch (e) {
        this.$emit('update:errorText', e.text());
      } finally {
        this.isActionLoading[action.label] = false;
      }
    },

    outsideClickHandler() {
      if (this.preventOutsideClick) this.shakeDialog();
      else this.closeDialog();
    },

    shakeDialog() {
      this.isShaking = true;
      this.stopShaking.async();
    },

    stopShaking() {
      this.isShaking = false;
    },

    closeDialog() {
      this.$emit('input', false);
    },
  },

  watch: {
    localValue: {
      immediate: true,
      handler(isOpened) {
        if (isOpened) this.$emit('opened');
        else this.$emit('closed');
      },
    },

    actions: {
      deep: true,
      immediate: true,
      handler() {
        this.actions.map(
          action => this.$set(
            this.isActionLoading,
            action.label,
            propOr(false, action.label, this.isActionLoading),
          ),
        );
      },
    },
  },

  created() {
    this.stopShaking.async = debounce(SHAKING_DURATION_MS, this.stopShaking);
  },
};
</script>

<style lang="stylus">
@import '~styles/common';

.c-dialog {
  z-index: 100;
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  top: 0;
  display: flex;

  transition-property: z-index;
  transition-duration: 0s;
  transition-timing-function: step-end;
  transition-delay: 0.3s;

  &_opened {
    z-index: 1;

    transition-duration: 0.3s;
    transition-timing-function: step-start;
    transition-delay: 0s;
  }

  &__overlay {
    z-index: 3;
    pointer-events: auto;
    touch-action: none;

    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba($base-text-color, .46);

    &-invisible {
      opacity: 0;
    }
  }

  &__window {
    z-index: 3;
    position: relative;
    flex: 0 0 auto;

    pointer-events: all;
    touch-action: auto;

    max-height: 90%;
    max-width: "calc(100% - %s)" % ($edge-gap * 2);
    margin: auto;

    outline: none;
    box-shadow:
        0   11px 15px -7px rgba(0, 0, 0, .2),
        0px 24px 38px 3px  rgba(0, 0, 0, .14),
        0px 9px  46px 8px  rgba(0, 0, 0, .12);

    border-radius: 4px;
    overflow-y: hidden;

    &_z-shaking {
      animation-name: z-shake-dialog;
      animation-timing-function: cubic-bezier(0.25, 0.8, 0.25, 1);
      animation-duration: 0.15s;
    }
  }
}

.c-window {
  display: grid;
  grid-template-rows: auto 1fr auto;
  grid-template-columns: auto 1fr auto;
  grid-template-areas: "h h h h" "s c c r" "s a a r";

  overflow: auto;

  background-color: white;

  &__header {
    grid-area: h;

    min-width: 0;
    max-width: 100%;
  }
  &__header,
  &__title {
    user-select: none;
  }

  &__status {
    margin-left: $module * 2;
    color: _rgba($contrast-rgb, .5);
  }

  &__title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: $module * 16;
    padding-left: $edge-gap;
    padding-right: $edge-gap;
    margin-top: 0;
    margin-bottom: 0;

    line-height: 24px;
    font-size: 20px;
    font-weight: 500;

    color: $contrast;
    background-color: $primary;
  }

  &__message {
    .c-alert {
      border-radius: 0;
    }
  }

  &__toolbar {
    border-bottom: 1px solid $theme-light-1;
  }

  &__sidebar {
    position: relative;
    grid-area: s;
    display: flex;
    background-color: #f5f5f5;

    &:before {
      content: "";
      position: absolute;
      top: 0;
      bottom: 0;
      right: 0;
      width: 1px;
      background-color: $theme-light-1;
    }
  }

  &__content {
    grid-area: c;
    padding: $edge-gap;

    &_no-frame {
      padding: 0;
    }
  }

  &__actions {
    display: flex;
    grid-area: a;
    min-height: 52px;
    align-items: center;
    justify-content: flex-end;
    padding-left: $edge-gap - ($module * 2);
    padding-right: $edge-gap - ($module * 2);
    border-top: 1px solid $theme-light-1;

    &_no-divider {
      border-top-color: transparent;
    }

    button {
      margin: 0;
    }

    button + button {
      margin-left: $module * 4;
    }
  }
}

@keyframes z-shake-dialog {
  0% {
      transform: scale(1);
  }
  50% {
      transform: scale(1.03);
  }
  100% {
      transform: scale(1);
  }
}
</style>
