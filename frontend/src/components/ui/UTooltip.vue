<template>
  <span class="ui-tooltip"
  :class="{
    invisible: icon == 'empty',
    noicon: icon == 'none',
    ['tooltip-on' + mode]: true
  }"
  @mouseenter="mouseenter"
  @mouseout="mouseout">
    <slot name="default" :props="$props">
      <UIcon :name="icon == 'empty' || icon == 'none' ? 'info-circle-empty' : icon" />
      <slot name="extendedText"></slot>
      <span class="tooltip" ref="tooltip"><span v-text="text"></span><span class="triangle"></span></span>
    </slot>
  </span>
</template>

<style lang="less" scoped>
.ui-tooltip {
  @s: .875rem;
  @triangleSize: 4px;
  @bg: #1f2d3d;
  @restrict: 20rem;

  position: relative;
  cursor: help;
  user-select: none;
  display: inline-block !important;
  vertical-align: top;
  margin-right: .5rem;
  overflow: hidden;

  &.invisible {
    opacity: 0;
    cursor: auto;
  }
  &.noicon .svg-icon { opacity: 0 !important; }
  .tooltip {
    position: absolute;
    padding: .75rem 1rem;
    border-radius: @border-radius;
    visibility: hidden;
    opacity: 0;
    transition: opacity .4s ease, visibility .4s ease;
    color: @col-text-light;
    font-size: .875rem;
    background: @bg;
    z-index: 5;
    text-transform: none;
    white-space: normal;
    display: block;
    line-height: 1.2rem;
    font-weight: 500;
    max-width: @restrict;
    width: max-content;

    
    .triangle {
      display: block;
      width: 0;
      height: 0;
      position: absolute;
      border: @triangleSize solid transparent;
    }
  }

  &.tooltip-onright .tooltip {
    bottom: @s/2;
    right: -@triangleSize;
    transform: translate(100%, 50%);
    max-height: @restrict;

    .triangle {
      left: -@triangleSize*2;
      top: calc(50% - @triangleSize);
      border-right-color: @bg;
    }
  }

  &.tooltip-onleft .tooltip {
    bottom: @s/2;
    left: -@triangleSize;
    transform: translate(-100%, 50%);
    max-height: @restrict;

    .triangle {
      right: -@triangleSize*2;
      top: calc(50% - @triangleSize);
      border-left-color: @bg;
    }
  }

  &.tooltip-ontop .tooltip {
    left: @s/2;
    top: -@triangleSize;
    transform: translate(-50%, -100%);

    .triangle {
      bottom: -@triangleSize*2;
      left: calc(50% - @triangleSize);
      border-top-color: @bg;
    }
  }

  &.tooltip-onbottom .tooltip {
    left: @s/2;
    bottom: -@triangleSize;
    transform: translate(-50%, 100%);

    .triangle {
      top: -@triangleSize*2;
      left: calc(50% - @triangleSize);
      border-bottom-color: @bg;
    }
  }


  &:hover {
    overflow: visible;
    
    .tooltip {
      visibility: visible;
      opacity: 1;
    }
  }
  &, .svg-icon {
    width: @s;
    min-width: @s;
    height: @s;
    min-height: @s;
  }
  .svg-icon { margin: 0; }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';
export default defineComponent({
  props: {
    text: { default: '', type: String },
    icon: { default: 'info-circle-empty', type: String },
    mode: { default: 'top', type: String } // can be top, bottom, left, right
  },
  methods: {
    fixPosition() {
      const SCREEN_PADDING = 10;

      const tooltip = <HTMLSpanElement>this.$refs.tooltip;
      const triangle = <HTMLSpanElement>tooltip.querySelector('.triangle');
      const br = tooltip.getBoundingClientRect();

      if (this.mode == 'top' || this.mode == 'bottom') {
        if (br.x < 0) {
          const parentBr = tooltip.parentElement?.getBoundingClientRect();
          const css = window.getComputedStyle(tooltip, null);

          triangle.style.left = `calc(${ br.x + br.width/2 }px - ${ css.paddingLeft } + ${ (parentBr?.width || 0) / 2 }px)`;
          tooltip.style.left = SCREEN_PADDING - br.x + 'px';

          return;
        }
        else if (br.x + br.width > window.innerWidth) {
          const parentBr = tooltip.parentElement?.getBoundingClientRect();
          const css = window.getComputedStyle(tooltip, null);

          const offScreenOffset = br.x + br.width - window.innerWidth;
          triangle.style.left = `calc(${ br.x + br.width/2 }px - ${ (parentBr?.width || 0) / 2 }px)`;
          tooltip.style.left = `calc(${ css.left } - ${ offScreenOffset + SCREEN_PADDING }px)`;

          return;
        }
      }
      else if (this.mode == 'left' || this.mode == 'right') {
        let screenOffset = 0;

        if (br.x < 0)
          screenOffset = -br.x + SCREEN_PADDING;

        else if (br.x + br.width > window.innerWidth)
          screenOffset = br.x + br.width - window.innerWidth + SCREEN_PADDING;

        if (screenOffset)
          tooltip.style.maxWidth = br.width - screenOffset + 'px';
      }
    },
    mouseenter() {
      this.fixPosition();
    },
    mouseout() {
      setTimeout(() => {
        const tooltip = <HTMLSpanElement>this.$refs.tooltip;
        const triangle = <HTMLSpanElement>tooltip.querySelector('.triangle');
        const css = window.getComputedStyle(<HTMLSpanElement>tooltip.parentElement, null);

        if (css.overflow == 'hidden') {
          tooltip.removeAttribute('style');
          triangle.removeAttribute('style');
        }
      }, 350);
    }
  }
})
</script>