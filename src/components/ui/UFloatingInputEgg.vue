<template>
  <div class="ui-floating-input">
    <input tabindex="-1" aria-hidden="true" style="visibility: hidden; position: absolute; top:0; left: 0;" :name="name" v-if="!name.startsWith('input__')">
    <input
      autocomplete="new-password"

      :id="id"
      :class="{ dirty: egg.dirty, invalid: egg.invalid }"

      :type="type || 'text'"
      :name="name"
      :readonly="egg.readonly || readonly"
      :disabled="egg.disabled || disabled"
      :step="step"
      placeholder=" "

      @focus="onFocus"
      @blur="onBlur"
      @input="onInput"

      v-model="internalValue"
      v-bind="appendAttributes"
      ref="input"

    >
    <label :for="id" v-text="label"></label>

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
  </div>
</template>

<style lang="less" scoped>
// Using https://dev.to/felix/floating-input-placeholders-with-html-css-ej4

@lh: 30px;
@lscale: 0.8;
.label-up { transform: translate(0, -(@lh * @lscale)) scale(@lscale); }
.label-down { transform: translate(0) scale(1); }

.ui-floating-input {
  @h: 50px;

  position: relative;
  display: inline-block;
  min-width: 100px;
  margin-top: 10px;

  &[disabled] {
    background: @col-disabled;

    > label { display: none; }
  }
  input {
    width: 100%;
    height: @h;
    line-height: @h;
    padding: 0 20px;
    border-radius: @border-radius;
    box-shadow: 0 0 0 1px @col-gray;
    transition: box-shadow 0.2s ease;
    border: none;
    outline: 0;
    font-weight: inherit;
    font-size: inherit;

    &:focus { box-shadow: 0 0 0 2px @col-text-dark; }
    &.dirty.invalid { box-shadow: 0 0 0 1.5px @col-err; }
    &[disabled] {
      background: @col-disabled;
      box-shadow: 0 0 0 1px @col-disabled;
    }
    &[readonly] { font-weight: 600; }
  }
  label {
    display: block;
    position: absolute;
    top: @h/2 - @lh/2;
    left: 10px;
    height: @lh;
    line-height: @lh;
    background: @col-bg;
    color: @col-text-gray-dark;
    border-radius: @border-radius;
    padding: 0 10px;
    will-change: transform;
    transform-origin: left;

    .label-up();

    + .ui-input-validation-error { margin-top: 5px; }
  }

  @supports (not (-ms-ime-align:auto)) {
    label {
      .label-down();
      transition: all 0.2s ease;
    }
      
    input:focus + label,
    input:not(:placeholder-shown) + label {
      .label-up();
      line-height: @lh * @lscale;
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
    label: { type: String, required: true },
    step: Number,
    type: String,
  },
  data() {
    return {
      id: 'input_id_' + Date.now() + '__' + Math.round(Math.random() * 100)
    }
  },
  mounted() {
    this.internalValue = this.egg.getValue();

    if (this.type == 'number') {
      (<any>this.$refs.input).addEventListener('keydown', function (ev:KeyboardEvent) {
        if (['+', 'e'].includes(ev.key))
          ev.preventDefault();
      });
      this.appendAttributes['pattern']='[0-9]*'
      this.appendAttributes['inputmode']='numeric'
    }
  }
})
</script>