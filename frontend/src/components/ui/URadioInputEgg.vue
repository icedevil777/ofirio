/**
 * @usage:
 *
 *   <URadio value="value_name" name="input_name" v-model="model">Label</URadio>
 *
 */

<template>
  <div class="ui-radio">
    <label class="flex" :class="{ active: isChecked }"><input
      type="radio"
      v-bind="$attrs"
      :checked="isChecked"
      :value="value"
      @change="(e) => egg.value = e.target.value"
      ><span></span><slot></slot></label>
  </div>
</template>


<style lang="less" scoped>

.ui-radio {
  @pad: 10px;
  @h: 40px;

  height: @h;
  padding: 0 @pad;
  position: relative;
  display: inline-block;

  label {
    height: 100%;
    align-content: center;
    align-items: center;
    justify-content: flex-start;
    font-size: 0.875rem;
    user-select: none;
    cursor: pointer;
    padding-left: 36px;

    &.active { font-weight: 700; }

    @media @mobile { font-size: 1rem; }
  }
  input {
    position: absolute;
    width: 0;
    height: 0;
    opacity: 0;
  }
  span {
    @s: 26px;
    @b: 2px;

    &:after, &:before {
      content: '';
      display: block;
      position: absolute;
      left: @pad;
      top: @h/2 - @s/2;
      border-radius: 50%;
    }
    &:before {
      background-color: transparent;
      width: @s - 2*@b;
      height: @s - 2*@b;
      border: @b solid @col-gray;
      transition: border-color .2s ease;
    }
    &:after {
      @s-small: 14px;
      width: @s-small;
      height: @s-small;
      top: @h/2 - @s-small/2;
      left: @pad + @s/2 - @s-small/2;
      background-color: @col-blue;
      transform: scale(0);
      transition: transform 0.2s ease-out;
    }
  }
  input:focus + span:before,
  input:active + span:before,
  input:checked + span:before,
  &:hover span:before {
    border-color: @col-blue;
  }
  input:checked + span:after { transform: scale(1); }
}

</style>


<script lang="ts">
import { defineComponent } from 'vue';
import { EggInputModel } from '@/models/Henhouse/Egg.mixin';

export default defineComponent({
  mixins: [ EggInputModel ],

  props: {
    jitter: { default: 'reactive '},
    value: { required: true }
  },
  computed: {
    isChecked():Boolean {
      return this.egg.value == this.value;
    }
  }
});
</script>