<template lang="pug">
.centerize(:style="fullscreen ? `height: calc(100vh - ${moveUp}px)` : ''")
  svg.connect-loader-icon(
    xmlns="http://www.w3.org/2000/svg",
    viewBox="0 0 24 24",
    :width="size",
    :height="size",
  )
    circle.connect-loader-icon__circle(
      cx="12",
      cy="12",
      r="8",
      :style="{ stroke: color }",
      stroke-dasharray="50 100",
      stroke-dashoffset="-17",
    )
      animateTransform(
        attributeType="xml"
        attributeName="transform"
        type="rotate"
        from="0 12 12" to="360 12 12" dur="2s"
        repeatCount="indefinite",
      )
      animate(
        attributeName="stroke-dasharray",
        dur="1.7s",
        calcMode="spline",
        repeatCount="indefinite",
        values="0 100; 50 100; 50 100",
        keyTimes="0; 0.7; 1",
        keySplines="0.42 0 0.58 1; 0.42 0 0.58 1",
      )
      animate(
        attributeName="stroke-dashoffset",
        dur="1.7s",
        calcMode="spline",
        repeatCount="indefinite",
        values="0; -17; -49.9",
        keyTimes="0; 0.7; 1",
        keySplines="0.42 0 0.58 1; 0.42 0 0.58 1",
      )
</template>

<script>
export default {
  props: {
    size: {
      type: String,
      default: '24',
    },

    fullscreen: Boolean,

    color: {
      type: String,
      default: '#1565C0',
    },

    moveUp: {
      type: String,
      default: '0',
    },
  },
};
</script>

<style lang="stylus">
.connect-loader-icon__circle {
  fill: none;
  stroke-width: 2px;
  stroke-linecap: butt;
}

.centerize {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
