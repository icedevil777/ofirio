/**
 * @usage:
 *
 *   <UTextInput value="value_name" name="input_name" v-model="model">Label</UTextInput>
 *
 */

<template>
  <div class="ui-input flex" v-bind:class="{ focused: isFocused, autoWidth: flexible, withLabel: label != undefined }">
    <span class="const prepend" @click="dec"><UIcon name="minus" /></span>
    <span class="empty"></span>
    <span class="const prefix" v-if="prefix != undefined" v-text="prefix"></span>
    <span class="label" v-if="label != undefined" v-text="label"></span>
    <div class="input-wrapper" @click="$refs.input.focus()">
      <span class="expander" v-text="modelValue" v-bind:class="{ wider: $attrs.type == 'number' }"></span>
      <input tabindex="-1" aria-hidden="true" style="display: none;">
      <input
        ref='input'
        type="number"
        v-bind="$attrs"
        :min="min"
        :max="max"
        :step="step"
        :value = "modelValue"
        @input="updateModel"
        @focus="isFocused = !0"
        @blur="isFocused = !1"
      >
    </div>
    <span class="const postfix" v-text="postfix" v-if="postfix != undefined"></span>
    <span class="empty"></span>
    <span class="const postpend" @click="inc"><UIcon name="plus" /></span>
  </div>
</template>


<style lang="less" scoped>

.ui-incremental-height-mixin() {
  height: @h;

  .input-wrapper {
    height: @ih;

    input {
      height: @ih;
    }
  }
  span.label {
    left: @w;
    right: @w;
  }
  .prepend, .postpend {
    width: @w;
    min-width: @w;
    height: @h;
  }
}

.ui-input {
  @h: 40px;
  @ih: 40px;
  @w: 40px;
  
  padding: 10px 0;
  margin: 5px 0;
  position: relative;
  width: 100%;
  max-width: 100%;
  border-radius: @border-radius;
  box-shadow: 0 0 0 1px @col-gray;
  transition: box-shadow ease .15s;
  justify-content: center;
  align-content: center;
  align-items: center;

  &.autoWidth { width: fit-content; }
  &.focused { box-shadow: 0 0 0 2px @col-blue; }
  .const {
    white-space: nowrap;
    flex: 0 0 0%;

    .svg-icon {
      width: 10px;
      height: 10px;
    }
  }
  .prefix {
    padding-right: 2px;
    margin-left: 5px;
  }
  .postfix {
    padding-left: 2px;
    margin-right: 5px;
  }

  .prepend { border-right: 1px solid @col-gray; }
  .postpend { border-left: 1px solid @col-gray; }
  .prepend, .postpend {
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
  }
  .prefix, .postfix, .input-wrapper {
    font-weight: bold;
  }
  .empty { flex: 1 1; }

  span.label {
    position: absolute;
    top: 0;
    text-align: center;
    height: 26px;
    line-height: 26px;
    color: @col-text-gray-dark;
    font-size: .875rem;
    user-select: none;

    @media @mobile {
      font-size: .95rem;
      height: 20px;
      line-height: 30px;
    }
  }
  .input-wrapper {
    position: relative;
    overflow: hidden;
    text-align: center;
    padding: 0 1px;
    
    span.expander {
      white-space: nowrap;
      overflow: hidden;
      opacity: 0;

      &.wider { padding-right: 5px; }
    }
    input {
      position: absolute;
      top: 0;
      left: 0;
      height: @h;
      line-height: @h;
      width: 100%;
      border: 0;
      min-width: 0;
      padding: 0;
      font: inherit;

      &:focus { outline: 0; }
      &::-webkit-outer-spin-button,
      &::-webkit-inner-spin-button {
        appearance: none;
        margin: 0;
      }

      &[type=number] {
        -moz-appearance: textfield;
      }
    }
  }

  &.withLabel {
    @h: 60px;
    @ih: 20px;

    .ui-incremental-height-mixin();
    .input-wrapper, .prefix, .postfix {
      margin-top: 20px
    }
  }
  .ui-incremental-height-mixin();
}

</style>


<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({

  props: {
    modelValue: { default: 0, required: true },
    label: String,
    prefix: String,
    postfix: String,
    flexible: Boolean,
    step: { type: Number, default: 1 },
    min: Number,
    max: Number
  },
  data() {
    return {
      isFocused: false
    }
  },
  methods: {
    updateModel(ev:InputEvent) {
      const target = ev.target as HTMLInputElement;
      let value = parseFloat(target.value);

      value = Math.min(value, this.max != undefined ? this.max : Infinity);
      value = Math.max(value, this.min != undefined ? this.min : -Infinity)
      this.$emit('update:modelValue', value);
    },
    inc() {
      const newValue = Math.min(this.modelValue + this.step, this.max != undefined ? this.max : Infinity);

      this.$emit('update:modelValue', newValue);
    },
    dec() {
      const newValue = Math.max(this.modelValue - this.step, this.min != undefined ? this.min : -Infinity);

      this.$emit('update:modelValue', newValue);
    }
  }
});
</script>