<template>
  <div class="ui-toggle">
    <label class="flex">
      <input
        type="checkbox"
        v-bind="$attrs"
        :checked="egg.value"
        @change="(e) => egg.value = !egg.value"
      >
      <span class="label" v-text="egg.value ? enabledLabel : disabledLabel"></span>
      <span class="visual"></span>
    </label>
  </div>
</template>

<style lang="less" scoped>
.ui-toggle {
  position: relative;
  display: inline-block;

  label {
    @h: 26px;
    @p: 7px;
    @bs: 1px;

    align-content: center;
    align-items: center;
    justify-content: flex-start;
    font-size: 0.875rem;
    user-select: none;
    cursor: pointer;

    .label {
      margin-right: 15px;
      font-weight: 700;
      color: @col-text-gray-darker;
      transition: color .3s ease;
    }
    .visual {
      display: block;
      height: @h;
      border-radius: @h/2;
      background: @col-text-gray-light;
      width: 2 * @h;
      position: relative;
      box-shadow: 0 0 0 1px transparent;
      transition: box-shadow .3s ease;

      &:before {
        @s: @h - 2*@p;

        content: '';
        display: block;
        position: absolute;
        width: @s;
        height: @s;
        left: @p;
        top: @p;
        background: @col-bg;
        border-radius: 50%;
        transform: translateX(0);
        transition: transform .3s ease;
      }
    }
    input {
      position: absolute;
      width: 0;
      height: 0;
      opacity: 0;
    }
    input:focus ~ span.visual,
    input:checked ~ span.visual,
    input:active ~ span.visual,
    &:hover span.visual{
      box-shadow: 0 0 0 1px @col-blue;
    }
    input:checked ~ span.label { color: @col-blue; }
    input:checked ~ span.visual {
      background-color: @col-blue;

      &:before { transform: translateX(@h); }
    }
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';
import { EggInputModel } from '@/models/Henhouse/Egg.mixin';

export default defineComponent({
  mixins: [ EggInputModel ],

  props: {
    enabledLabel: { default: 'Enabled' },
    disabledLabel: { default: 'Disabled' },
  }
});
</script>