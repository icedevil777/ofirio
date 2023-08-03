<template>
  <div class="ui-input-textarea" v-bind:class="{ focused: isFocused, flexible, invalid: egg.dirty && egg.invalid }" @click="$refs.input.focus()">
    <textarea      
      :name="name"
      :readonly="egg.readonly || readonly"
      :disabled="egg.disabled || disabled"
      :placeholder="placeholder"

      @focus="onFocus"
      @blur="onBlur"
      @input="onInput"

      v-model="internalValue"
      v-bind="appendAttributes"

      ref='input'
    ></textarea>
  </div>
  <slot name="validation" :message="egg.errors[0]" :messages="egg.errors">
    <template v-if="!noValidationMessages && egg.dirty">
      <span
        class="ui-input-validation-error active"
        v-for="err of egg.errors"
        :key="err"
        v-text="err"
      ></span>
    </template>
  </slot>
</template>


<style lang="less" scoped>

.ui-input-textarea {
  @pad: 20px;

  padding: @pad;
  margin: 5px 0;
  width: 100%;
  max-width: 100%;
  border-radius: @border-radius;
  box-shadow: 0 0 0 1px @col-gray;
  transition: box-shadow ease .15s;

  &.focused { box-shadow: 0 0 0 2px @col-text-dark; }
  &.invalid { box-shadow: 0 0 0 1.5px @col-err; }
  &.flexible { width: fit-content; }
  textarea {
    line-height: inherit;
    width: 100%;
    border: 0;
    min-width: 0;
    padding: 0;
    font: inherit;
    min-height: 40px;
    resize: vertical;
    background: transparent;

    &:focus { outline: 0; }
    &::placeholder { font-weight: 500; }
  }

}

</style>


<script lang="ts">
import { defineComponent } from 'vue';
import { EggInputModel } from '@/models/Henhouse/Egg.mixin';

export default defineComponent({
  mixins: [EggInputModel],
  props: {
    jitter: { default: 'blur' }
  }
});
</script>