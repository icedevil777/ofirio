<template>
  <slot name="icons" class="icons" v-if="mode == 'prepend'">
    <UIcon v-if="!isCopied" name="copy" @click="copyToClipboard" class="copy"/>
    <UIcon v-if="isCopied" name="checked-circle" class="checkmark" />
  </slot>
  <slot :props="{ copyToClipboard }"></slot>
  <slot name="icons" class="icons" v-if="mode == 'postpend'">
    <UIcon v-if="!isCopied" name="copy" @click="copyToClipboard" class="copy"/>
    <UIcon v-if="isCopied" name="checked-circle" class="checkmark" />
  </slot>
</template>
<style lang="less" scoped>
  .svg-icon {
    @s: 16px;
    width: @s;
    height: @s;
    margin: 0 @s 0 0;
    cursor: pointer;

    @media @mobile {
      margin: 5px @s 0;
    }
  }
  .copy { fill: @col-text-gray-darker; }
  .checkmark { fill: @col-green; }
</style>
<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({
  data() {
    return {
      isCopied: false
    }
  },
  props: {
    text: { type: String, required: true },
    mode: { type: String, default: 'postpend' }
  },
  methods: {
    copyToClipboard() {
      if (this.isCopied)
        return

      navigator.clipboard.writeText(this.text);
      this.isCopied = true;
      setTimeout(() => { this.isCopied = false; }, 3000);
    }
  }
})
</script>