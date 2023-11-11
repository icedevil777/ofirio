/**
 * @usage:
 *
 *   <UCheckbox value="value_name" name="input_name" v-model="model">Label</UCheckbox>
 *
 */

<template>
  <div class="ui-checkbox">
    <label class="flex"><input
      type="checkbox"
      v-bind="$attrs"
      :checked="isChecked"
      @change="updateModel"
      ><span></span><slot></slot></label>
  </div>
</template>


<style lang="less" scoped>

.ui-checkbox {
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
    }
    &:before {
      background-color: transparent;
      width: @s - 2*@b;
      height: @s - 2*@b;
      border-radius: @border-radius;
      border: @b solid @col-gray;
      transition: background-color .1s ease, border-color .2s ease;
    }
    &:after {
      width: @s;
      height: @s;
      background-image: url('/icons/statfix-icons/checked-fff.svg');
      background-position: center;
      background-repeat: no-repeat;
      background-size: 12px;
      transform: scale(0.7);
      transition: transform 0.2s ease-out;
    }
  }
  input:focus + span:before,
  input:checked + span:before,
  input:active + span:before,
  &:hover span:before {
    border-color: @col-blue;
  }
  input:checked + span {
    &:before { background-color: @col-blue; }
    &:after { transform: scale(1); }
  }
}

</style>


<script lang="ts">
import { defineComponent } from 'vue';
import { EggMultiChoiseInputModel } from '@/models/Henhouse/Egg.mixin';

export default defineComponent({
  mixins: [EggMultiChoiseInputModel],
  methods: {
    updateModel(ev:InputEvent) {
      const target = ev.target as HTMLInputElement;
      const isChecked = target.checked;

      if (this.value) {
        if (isChecked)
          this.egg.rawValue.push(this.value);
        else
          this.egg.rawValue.splice(this.egg.rawValue.indexOf(this.value), 1);
      } else
        this.egg.rawValue = !!isChecked;
    }
  }
});
</script>