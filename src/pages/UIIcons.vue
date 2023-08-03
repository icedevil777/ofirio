<template>
  <div class="wrapper">
    <div v-for="icon of icons" :key="icon" class="icon-wrapper">
      <UIcon :name="icon" />
      <span>{{ icon }}</span>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  data() {
    const icons = require.context(
      '@/assets/icons',
      true,
      /^.*\.svg$/
    )

    let formattedIcons = [];
    for (let i = 0; i < icons.keys().length; i++)
      formattedIcons[i] = icons.keys()[i].slice(2, -4);

    return {
      icons: formattedIcons
    }
  }
})
</script>

<style lang="less" scoped>
  .wrapper {
    margin-top: 30px;
    display: grid; 
    grid-template-columns: 1fr 1fr 1fr 1fr 1fr 1fr; 
    gap: 30px 30px; 
  }
  .icon-wrapper {
    aspect-ratio: 1;
    text-align: center;
    background: @col-text-gray-light;
    border-radius: @border-radius;

    &:hover { color: @col-blue; }
  }
  span {
    display: block;
    margin-top: 10px;
  }
  .svg-icon {
    @s: 60px;

    width: @s;
    height: @s;
    margin-top: 30%;
  }
</style>