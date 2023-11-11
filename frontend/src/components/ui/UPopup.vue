<template>
  <div
    class="ui-popup flex"
    v-bind:class="{ opened: isOpen }"
    @click.stop="close"
    ref="popupWrapper"
  >
    <slot></slot>
  </div>
</template>


<style lang="less" scoped>
.ui-popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: calc(100*var(--vh));
  opacity: 0;
  visibility: hidden;
  transition: opacity .4s cubic-bezier(0, 0, 0.2, 1), visibility .4s ease;
  background: @col-popup-bg;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  z-index: 100000;

  &.opened {
    opacity: 1;
    visibility: visible;
    // &, & .content {
    //   opacity: 1;
    //   visibility: visible;
    // }
    // .content { transform: scale(1); }
  }
  &::v-deep > div {
    background: @col-bg;
    max-width: 900px;
    border-radius: @border-radius;

    @media @mobile { border-radius: 0 }
  }
  &::v-deep svg.ui-popup-default-close-icon {
    @s: 14px;
    @p: 20px;

    position: absolute;
    width: @s;
    height: @s;
    top: @p;
    right: @p;
    fill: @col-text-gray-darker;
    box-sizing: content-box;
    cursor: pointer;

    @media @mobile {
      @buffer: 20px - @s/2;
      @p: 10px;

      position: fixed;
      background: @col-disabled;
      padding: @buffer;
      border-radius: 50%;
      top: @p;
      right: @p;
    }
  }
}
</style>


<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  data() {
    return {
      isOpen: false
    }
  },
  methods: {
    // closeHander: function (e:MouseEvent) {
    //   if (!e.composedPath().includes(<any>this.$refs.container)) {
    //     e.stopImmediatePropagation();
    //     e.stopPropagation();
    //     e.preventDefault();
    //     this.close();
    //   }
    // },
    toggle() {
      return this.isOpen ? this.close() : this.open();
    },
    open() {
      this.isOpen = true;
      document.body.classList.toggle('no-scroll', this.isOpen);
      this.$emit('stateChange', true);
    },
    close(e?:MouseEvent) {
      if (e && e.target != this.$refs.popupWrapper)
        return;
        
      this.isOpen = false;
      document.body.classList.toggle('no-scroll', this.isOpen);
      this.$emit('stateChange', false);
    }
  }
});
</script>