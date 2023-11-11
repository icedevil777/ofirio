<template>
  <div class="breadcrumbs flex">
    <div class="mobile-mm" v-if="$isMobile.value"></div>
    <slot></slot>
    <div class="mobile-mm" v-if="$isMobile.value"></div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({})
</script>

<style lang="less" scoped>
.breadcrumbs {
  color: @col-text-gray-darker;
  font-size: .875rem;
  padding: 1rem 0 1.5rem;
  justify-content: flex-start;
  align-content: center;
  align-items: center;

  @media @mobile {
    width: 100%;
    padding: 0;
    overflow-x: auto;
    white-space: nowrap;
    height: 1rem;
  }
  ::v-deep {
    .ui-href-gray + .ui-href-gray {
      margin-left: 10px;

      &:before {
        content: '/';
        margin-right: 10px;
        color: #e5e5e5;
      }
    }
  }
}
</style>