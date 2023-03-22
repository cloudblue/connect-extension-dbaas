<template lang="pug">
.c-simple-toolbar__placeholder
  .c-simple-toolbar._display_flex-center
    c-simple-svg._ml_24._mr_24(
      v-if="onBack",
      path="arrow_back",
      @click="onBack",
    )

    ._display_flex-column
      .assistive-text(v-if="subtitle") {{ subtitle }}
      h3._mb_0  {{ title }}

    .c-simple-toolbar__actions._mr_24
      slot(name="actions")
</template>

<script>
import cSimpleSvg from '~components/cSimpleSvg.vue';


export default {
  components: {
    cSimpleSvg,
  },

  props: {
    onBack: Function,

    title: {
      type: String,
      default: '',
    },

    subtitle: String,
  },
};
</script>

<style lang="stylus">
@import '~styles/common';

._display_flex-column {
  display: flex;
  flex-direction: column;
}

.c-simple-toolbar {
  position: fixed;
  height: 64px;
  left: 0px;
  right: 0px;
  background: $theme-controls-background;
  border-bottom: 1px solid $theme-border-color;

  &__placeholder {
    height: 64px;
    width: 100%;
  }

  &__actions {
    margin-left: auto;
    display: flex;
    align-items: center;
    flex: 0 0 auto;
  }
}
</style>
