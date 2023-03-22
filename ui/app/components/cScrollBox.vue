<template lang="pug">
.scroll-box(
  ref="container",
  @scroll="onScroll",
)
  slot
</template>

<script>
export const ACCURACY = 5;


export default {
  data() {
    return {
      isScrollAtBottom: false,
      isScrollAtTop: false,
    };
  },

  methods: {
    // it is not computed, because props of refs are not watching;
    scrollBottom() {
      if (this.$refs.container) {
        const { scrollHeight, scrollTop, clientHeight } = this.$refs.container;

        return Math.abs(scrollHeight - clientHeight - scrollTop);
      }

      return undefined;
    },

    async isScrollHidden() {
      let isScrollHidden = true;
      await this.$nextTick();

      if (this.$refs.container) {
        const { scrollHeight, clientHeight } = this.$refs.container;

        isScrollHidden = scrollHeight <= clientHeight;
      }

      return isScrollHidden;
    },

    async checkScrollDown() {
      if (!this.$refs.container) return;

      const { scrollTop } = this.$refs.container;
      this.isScrollAtBottom = this.scrollBottom() < ACCURACY;
      this.isScrollAtTop = scrollTop < ACCURACY;

      const isScrollVisible = !await this.isScrollHidden();
      if (isScrollVisible) {
        if (this.isScrollAtBottom) this.$emit('scroll-at-bottom');
        if (this.isScrollAtTop) this.$emit('scroll-at-top');
      }
    },

    onScroll() {
      this.$emit('scroll', this.scrollBottom());
      this.checkScrollDown();
    },
  },
};
</script>

<style lang="stylus" scoped>
.scroll-box {
  position: relative;
  overflow-y: auto;
}
</style>
