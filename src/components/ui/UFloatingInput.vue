<template>
  <div class="ui-floating-input">
    <input tabindex="-1" aria-hidden="true" style="display: none;" :name="$attrs.name">
    <input
      v-bind="$attrs"
      :value = "innerModel"
      autocomplete="new-password"
      @input="updateModel"
      @focus="focused = true"
      @blur="focused = false; updateModel($event)"
      :id="id"
      placeholder=" "
      ref="input"
      v-bind:class="{ dirty, invalid: !valid }"
    >
    <label :for="id" v-text="label"></label>
    <span class="validationError" v-if="dirty && !valid" v-text="validationText"></span>
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
    appearance: none;

    &:focus { box-shadow: 0 0 0 2px @col-blue; }
    &.dirty.invalid { box-shadow: 0 0 0 1px @col-err; }
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

  .validationError {
    display: block;
    font-size: 0.875rem;
    margin: 5px 0;
    padding: 0 20px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: @col-err;
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';
import { debounce } from 'ts-debounce';

import IMask from 'imask';

const validateInput = debounce(async function (value: any, scheme: any) {
  try {
    const validated = await scheme.validate(value);
    return validated === value;
  } catch (ex) { return ex.errors; }
}, 250);

export default defineComponent({
  props: {
    modelValue: { default: '', required: true },
    label: String,
    mask: Object,
    scheme: Object
  },
  data() {
    return {
      id: 'input-id-' + (Math.random() * Date.now()).toFixed(0),
      dirty: false,
      valid: null as null|boolean,
      validationText: null as null|string,
      innerModel: '',
      focused: false,
      maskInstance: null as any
    }
  },
  methods: {
    updateModel(ev:InputEvent) {
      const target = ev.target as HTMLInputElement;
      const value = target.value;

      this.innerModel = value;
      this.dirty = true;
      this.valid = true;

      if (this.scheme && !this.focused)
        validateInput(value, this.scheme).then((res:any) => {
          this.valid = res === true;
          if (this.valid)
            return this.$emit('update:modelValue', value);
            
          this.validationText = res[0];
          this.$emit('update:modelValue', null);
        });
      else
        this.$emit('update:modelValue', value);
    }
  },
  watch: {
    'modelValue'(newVal) {
      if (newVal == null && this.valid == false)
        return;
        
      this.innerModel = newVal;
    }
  },
  mounted() {
    this.innerModel = this.modelValue;
    if (this.mask)
      this.maskInstance = IMask(<HTMLElement>this.$refs.input, <any>this.mask);
  },
  beforeUnmount() {
    if (this.maskInstance != null)
      this.maskInstance.destroy();
  }
})
</script>