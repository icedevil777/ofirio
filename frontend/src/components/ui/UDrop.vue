<template>
  <div class="ui-drop" :class="{ opened: isOpen }">
    <div class="ui-drop-label flex" @click="disabled ? undefined : toggle()">
      <slot name="label" :isOpen="isOpen" >
        <span v-text="label"></span>
        <UIcon name="smooth-arrow" />
      </slot>
    </div>
    <div class="ui-drop-container" ref="container">
      <div class="ui-drop-mHeader hide-desktop" v-text="mHeader" v-if="mHeader"></div>
      <div class="scroll-container">
        <slot name="content" :props="{ isOpen, close }"></slot>
      </div>
      <UIcon name="cross-bolder" class="hide-desktop" @click="close" />
    </div>
    <div class="ui-drop-conteiner-bg hide-desktop" @click="close"></div>
  </div>
</template>


<style lang="less" scoped>
.ui-drop {
  @h: 40px;
  @mhHeader: 50px;

  position: relative;

  .ui-drop-label {
    height: @h;
    line-height: @h;
    padding: 0 15px;
    box-shadow: 0 0 0 1px @col-gray-light;
    border-radius: @border-radius;
    justify-content: flex-start;
    align-items: center;
    width: fit-content;
    cursor: pointer;
    user-select: none;
    transition: all .3s ease;

    &:hover {
      box-shadow: 0 0 0 1px @col-text-dark;
    }
    &::v-deep .svg-icon--smooth-arrow {
      margin-left: 10px;
      width: 10px;
      height: 10px;
      transform: rotate(180deg);
      transition: transform .3s ease,;
    }
  }
  .ui-drop-mHeader {
    height: @mhHeader;
    line-height: @mhHeader;
    width: 100%;
    text-align: center;
    font-weight: 800;
    font-size: 1.14rem;
    border-bottom: 1px solid @col-gray;
  }
  .ui-drop-conteiner-bg {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: @col-popup-bg;
    z-index: 1200;
    opacity: 0;
    visibility: hidden;
  }
  .ui-drop-container {
    position: absolute;
    opacity: 0;
    top: @h + 20px;
    left: 50%;
    transform: translate(-50%, -20px);
    transition: transform .3s ease, opacity .2s ease, visibility .3s;
    visibility: hidden;
    border-radius: @border-radius;
    box-shadow: @shadow @col-shadow;
    background: @col-bg;

    @media @mobile {
      position: fixed;
      top: auto;
      bottom: 0;
      left: 0;
      width: 100%;
      transform: translateY(100%);
      z-index: 1300 !important;
      box-shadow: 0 0 0 @col-shadow;
      padding: 0;
      border-radius: @border-radius @border-radius 0 0;

      .scroll-container {
        max-height: calc(100*var(--vh) - 140px);
        overflow-y: auto;
      }
    }
    > .svg-icon--cross-bolder {
      @s: 12px;

      fill: @col-text-gray-darker;
      position: absolute;
      top: 0;
      right: 0;
      width: @s + 2*(@mhHeader/2 - @s/2);
      height: @mhHeader;
      padding: @mhHeader/2 - @s/2;
    }
  }

  &.opened {
    > .ui-drop-label {
      box-shadow: 0 0 0 2px @col-text-dark;
      background: lighten(@col-gray, 12%);
    }
    > .ui-drop-container,
    > .ui-drop-conteiner-bg {
      opacity: 1;
      visibility: visible;
    }
    > .ui-drop-container {
      transform: translate(-50%, 0);

      @media @mobile { transform: translateY(0); }
    }
    > .ui-drop-label::v-deep .svg-icon { transform: rotate(0); }
  }
}
</style>


<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  props: {
    label: String,
    disabled: { default: false, type: Boolean },
    mHeader: String
  },
  data() {
    return {
      isOpen: false
    }
  },
  methods: {
    closeHander: function (e:MouseEvent) {
      if (!e.composedPath().includes(<any>this.$refs.container)) {
        e.stopImmediatePropagation();
        e.stopPropagation();
        e.preventDefault();
        this.close();
      }
    },
    toggle() {
      return this.isOpen ? this.close() : this.open();
    },
    open() {
      this.isOpen = true;
      (<any>this).$isMobile.value && document.body.classList.toggle('no-scroll', this.isOpen);
      setTimeout(() => {
        if (this.isOpen)
          window.document.addEventListener('click', this.closeHander, true);
      }, 100);
    },
    close() {
      if (this.isOpen && (<any>this).$isMobile.value)
        document.body.classList.toggle('no-scroll', false);
      this.isOpen = false;
      window.document.removeEventListener('click', this.closeHander, true);
    }
  }
});
</script>