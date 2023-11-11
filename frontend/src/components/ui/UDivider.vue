<template>
  <div class="ui-divider" :data-label="label" v-bind:class="{ labelVisible }"></div>
</template>

<style lang="less" scoped>
  .ui-divider {
    height: 1px;
    position: relative;
    margin: 20px 0;
    width: 100%;
    background: @col-gray;

    &:before {
      width: 30px;
      height: 12px;
      line-height: 12px;
      background: @col-bg;
      position: absolute;
      left: calc(50% - 15px);
      text-align: center;
      top: -6px;
      font-size: 0.75rem;
      font-weight: bold;
      color: @col-text-gray-darker;
    }
    &.labelVisible:before {
      content: attr(data-label);
    }
  }
</style>

<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({
  props: {
    label: String
  },
  data() {
    return {
      labelVisible: false
    }
  },
  mounted() {
    if (this.label != undefined)
      this.labelVisible = true;
  }
})
</script>