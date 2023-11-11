<template>
  <div class="static-page-header">
    <div class="wrapper">
      <slot />
    </div>
    <img :class="{ top: wavePosition == 'top' }" src="@/assets/images/static/common/wavy-line.svg">
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  props: {
    wavePosition: { type: String, default: 'bottom' }
  }
})
</script>

<style lang="less" scoped>
  .static-page-header {
    position: relative;
    background-position: center;
    background-size: cover;
  
    .wrapper { padding: 15vh 0; }
    &::v-deep {
      .title {
        font-size: 3.125rem;
        font-weight: 800;
        color: @col-text-light;
      }
      .text {
        font-size: 1.25rem;
        font-weight: 600;
        line-height: 2rem;
        color: @col-disabled;
        margin-top: 25px;
      }
  
      @media @mobile {
        .wrapper { padding: 10vh 20px; }
        .title { font-size: 2.5rem; }
      }
    }
    > img {
      width: 100%;
      position: absolute;
      bottom: 0;

      &.top {
        bottom: auto;
        top: 0;
        transform: rotateX(180deg);
      }
    }
  }
</style>