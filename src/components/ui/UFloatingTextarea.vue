<template>
  <div class="ui-floating-textarea" :class="{ focused: isFocused, autoWidth: flexible, dirty, invalid: !valid }" @click="$refs.input.focus()">
    <textarea
      autocomplete="off"
      :id="id"
      ref='input'
      v-bind="$attrs"
      :value = "modelValue"
      @input="updateModel"
      @focus="isFocused = !0"
      @blur="isFocused = false; updateModel($event)"
      placeholder=" "
    ></textarea>
    <label :for="id" v-text="label"></label>
  </div>
</template>


<style lang="less" scoped>
// Using https://dev.to/felix/floating-input-placeholders-with-html-css-ej4

@lh: 30px;
@lscale: 0.8;
.label-up { transform: translate(0, -(@lh * @lscale)) scale(@lscale); }
.label-down { transform: translate(0) scale(1); }

.ui-floating-textarea {
  @pad: 20px;

  position: relative;
  padding: @pad;
  margin: 15px 0 5px;
  width: 100%;
  max-width: 100%;
  border-radius: @border-radius;
  box-shadow: 0 0 0 1px @col-gray;
  transition: box-shadow ease .15s;

  &.focused { box-shadow: 0 0 0 2px @col-blue; }
  &.dirty.invalid { box-shadow: 0 0 0 1px @col-err; }
  &[disabled] {
    background: @col-disabled;
    box-shadow: 0 0 0 1px @col-disabled;

    > label { display: none; }
  }
  &[readonly] { font-weight: 600; }
  &.autoWidth { width: fit-content; }

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
  }


  label {
    @h: 50px;

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
  }

  @supports (not (-ms-ime-align:auto)) {
    label {
      .label-down();
      transition: all 0.2s ease;
    }
      
    textarea:focus + label,
    textarea:not(:placeholder-shown) + label {
      .label-up();
      line-height: @lh * @lscale;
    }
  }

}
</style>


<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({

  props: {
    modelValue: { default: '', required: true },
    label: { default: '', type: String },
    flexible: Boolean,
  },
  data() {
    return {
      isFocused: false,
      id: 'input-id-' + (Math.random() * Date.now()).toFixed(0),
      dirty: false,
      valid: null as null|boolean
    }
  },
  methods: {
    updateModel(ev:InputEvent) {
      const target = ev.target as HTMLInputElement;
      const value = target.value;
      this.$emit('update:modelValue', value);
    }
  }
});
</script>