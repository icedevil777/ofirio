<template>
  <table class="fin-table">
    <slot></slot>
  </table>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
})
</script>

<style lang="less" scoped>
.fin-table {
  border: none;
  border-radius: @border-radius;
  border-collapse: collapse !important;
  table-layout: fixed;
  border-style: hidden;
  box-shadow: 0 0 0 1px @col-gray;
  width: 100%;

  &::v-deep {
    > tr > td {
      border: 1px solid @col-gray;
      padding: 0;
      position: relative;
    }
    .centering {
      justify-content: space-between;
      align-items: center;
    }
    .char {
      padding: 1rem;
      font-weight: 700;
      white-space: nowrap;

      .title {
        display: flex;
        flex-wrap: nowrap;
        font-size: .75rem;
        height: .875rem;
        line-height: .875rem;
        font-weight: 600;
        color: @col-text-gray-dark;
        text-transform: uppercase;
        justify-content: flex-start;
        align-items: center;
        text-decoration: underline dashed #c6c6c6;
        text-underline-offset: 2px;
        position: relative;

        .ui-tooltip {
          margin-right: .25rem;

          @media @mobile {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            margin: 0;
          }
        }
      }
      .value {
        font-size: 1.25rem;
        margin-bottom: .5rem;
      }
    }
    .bottom-action {
      justify-content: center;
      align-items: center;
      align-content: center;
      background: @col-gray-light;
      padding: 0.75rem 0;
      border-radius: 0 0 @border-radius @border-radius;
      width: 100%;
      text-transform: uppercase;
      font-size: 0.75rem;
      color: @col-text-gray-dark;
      font-weight: 700;
      margin: 0;

      .svg-icon {
        margin-right: 10px;
        fill: @col-text-gray-dark;
      }
    }
  }
}
</style>
