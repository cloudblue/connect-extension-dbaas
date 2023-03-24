<template lang="pug">
.c-table(
  :class="{'c-table-loading': loading}",
)
  .table-relative
    .c-table__overflow
      table(
        v-if="columns.length",
        ref="table",
        :locator="locator",
        :class=`{
          'c-table_layout_fixed': fixLayout,
          'c-table_loading': loading,
          'c-table_dense': dense,
        }`,
      )
        thead
          tr
            th(v-for="column in columns", :key="`${column.value}_header`")
              slot(:name="`${column.value}-header`", v-bind="column")
                span {{ column.name || column.value }}

        tbody
          template(v-if="loading")
            tr.c-table__loader(v-for="row in 10", :key="row")
              td(v-for="column in columns", :key="column.value")
                div.c-table__loader_skeleton(:style="`width: ${random(50, 100)}%`")

          template(v-else-if="!loading && value.length")
            tr(v-for="(item, index) in value", :key="index")
              td(v-for="column in columns", :key="`${column.value}_column`")
                slot(
                  :name="column.value",
                  v-bind="{ column, item, value: dpath(column.value, item) }",
                )
                  span {{ dpath(column.value, item) }}

          template(v-else)
            tr
              td.text-xs-center(:colspan="columns.length") No data available
</template>

<script>
import {
  identity,
} from 'ramda';

import {
  dpath,
  random,
} from '~utils';


export default {
  props: {
    value: Array,
    columns: Array,
    loading: Boolean,
    fixLayout: Boolean,
    dense: Boolean,
    locator: String,

    prepareRow: {
      type: Function,
      default: identity,
    },
  },

  methods: {
    dpath,
    random,
  },
};
</script>

<style lang="stylus">
@import '~styles/variables';

.fade-enter-active {
  transition: opacity .4s ease-out;
}
.fade-leave-active {
  transition: opacity .4s ease-in;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}

.c-table {
  position: relative;

  &_layout_fixed {
    table-layout: fixed;
  }

  &_loading tr:hover {
    background: none !important;
  }

  &_dense tbody tr td {
    height: 32px;
  }

  &__overflow{
    width: 100%;
    overflow-x: auto;
    overflow-y: hidden;
  }

  table {
    border-collapse: collapse;
    border-spacing: 0;
    width: 100%;
    max-width: 100%;
  }

  &__loader {
    &_skeleton {
      border-radius: 8px;
      background: #d9d9d9;
      height: 12px;
      max-width: 100%;
    }

    animation: aniVertical 3s ease;
    animation-iteration-count: infinite;
    animation-fill-mode: forwards;
    opacity: 1;

    &:nth-child(2) {
      animation-delay: .5s;
    }

    &:nth-child(3) {
      animation-delay: 1s;
    }
    &:nth-child(4) {
      animation-delay: 1.5s;
    }

    &:nth-child(5) {
      animation-delay: 2s;
    }

    &:nth-child(6) {
      animation-delay: 2.5s;
    }

    &:nth-child(7) {
      animation-delay: 3s;
    }

    &:nth-child(8) {
      animation-delay: 3.5s;
    }

    &:nth-child(9) {
      animation-delay: 4s;
    }

    &:nth-child(10) {
      animation-delay: 4.5s;
    }
  }

  &__pagination.disabled {
    pointer-events: none;
    opacity: 0.3;
    filter: grayscale(100%);
  }

  th,td {
    box-sizing: content-box;
  }

  th {
    text-align: left;
  }

  td {
    height: 48px;
    font-size: 14px;
    padding-right: 12px;
    padding-left: 12px;

    .date-item {
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }

    .detail-item {
      &__assistive-text, &__text {
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }
    }

    a, .status-mark {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .assistive-text {
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
  }

  th {
    &:first-child {
      border-left: none;
    }

    &:last-child {
      border-right: none;
    }
  }

  thead {
    border-top: 1px solid #e0e0e0;
    border-bottom: 1px solid #e0e0e0;
    background-color: #f5f5f5;

    th {
      overflow: hidden;
      height: 32px;
      min-height: 32px;
      padding-right: $module * 3;
      padding-left: $module * 3;
      font-size: 12px;
      line-height: 20px;
      letter-spacing: 0.5px;
      color: $assistive-text-color;
      text-transform: uppercase;
    }
  }

  tbody > tr {
    &:not(:last-child) {
      border-bottom: 1px solid $light-grey;
    }

    &:last-child td {
      border-bottom: none;
    }
  }

  &__panel {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 48px;

    &.disabled {
      pointer-events: none;
      opacity: 0.3;
      filter: grayscale(100%);
    }

    &_bottom {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      height: 48px;
      border-top: 1px solid #e0e0e0;
    }
  }
  &__panel-actions{
    margin-left: -8px;
    display: flex;
    align-items: center;
  }
  &__panel-button {
    margin: 0 12px 0 0;

    .c-table_buttons &:last-child {
      margin: 0;
    }

    &_active.c-button {
      color: $accent;
      caret-color: $accent;
      &:before {
        background-color: currentColor;
      }
    }
  }

  &_dragging {
    user-select: none;
  }
}
.table-relative {
  position: relative;
}
.semi-transparent-overlay {
  tbody {
    opacity: 0.5;
    pointer-events: none;
  }
}

.progress-spinner {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  top: 0;
  z-index: 2;
  margin: auto;
  width: 32px !important;
  height: 32px;
  padding: 6px;

  background-color: #ffffff;

  border-radius:50%;
  box-shadow: 0 0 15px 1px #888888;
}

.splitpane {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 8px !important;
  padding-top: 4px;
  padding-bottom: 4px;
  cursor: col-resize;

  &:after {
    content: "";
    display: block;
    width: 1px;
    height: 100%;
    margin-left: auto;
    margin-right: auto;

    border-radius: 2px;
    background-color: #e0e0e0;
  }

  &_hovered:after,
  &:hover:after {
    width: 4px;
    background-color: $accent;
  }
}

@keyframes aniVertical {
  0% {
    opacity: 1;
  }

  50% {
    opacity: .6;
  }

  100% {
    opacity: 1;
  }
}
</style>

