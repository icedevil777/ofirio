/**
 * @usage:
 *
 *   <UTextInput value="value_name" name="input_name" v-model="model">Label</UTextInput>
 *
 */

<template>
  <div class="ui-input flex" v-bind:class="{ focused: isFocused, autoWidth: flexible, vertical }" @click="focus">
    <span class="const prepend" v-if="prepend != undefined" v-text="prepend"></span>

    <div class="vertical-container flex" v-if="vertical">
      <span class="const prefix" v-if="prefix != undefined" v-text="prefix" v-show="!formatter || (formatter && isFocused)"></span>
      <div class="input-wrapper"><span v-text="formatValue(internalModelValue)" v-bind:class="{ wider: $attrs.type == 'number' }" :style="{ opacity: !formatter || (formatter && isFocused) ? 0 : 1 }"></span>
        <slot name="input" :update="updateModel" :isFocused="isFocused">
          <input tabindex="-1" aria-hidden="true" style="display: none;" :name="$attrs.name">
          <input
            ref='input'
            v-bind:type="type"
            v-bind:readonly="readonly"
            v-bind:disabled="disabled"
            v-bind:pattern="pattern"
            v-bind:min="min"
            v-bind:max="max"
            v-bind:step="step"
            v-bind:placeholder="placeholder"
            v-bind:data-hj-allow="dataHjAllow"
            v-bind="customAttrs"
            v-model="internalModelValue"
            @input="processValue"
            @focus="onFocus"
            @blur="onBlur"
            @keyup.enter="updateModel(), $emit('enter')"
            :style="{ opacity: formatter && !isFocused ? 0 : 1 }"
            autocomplete="new-password"
          >
        </slot>
      </div>
      <div class="empty"></div>
      <span class="const postfix" v-if="postfix != undefined" v-text="postfix" v-show="!formatter || (formatter && isFocused)"></span>
    </div>

    <span class="const prefix" v-if="!vertical && prefix != undefined" v-text="prefix" v-show="!formatter || (formatter && isFocused)"></span>
    <div class="input-wrapper" v-if="!vertical"><span v-text="formatValue(internalModelValue)" v-bind:class="{ wider: $attrs.type == 'number' }" :style="{ opacity: !formatter || (formatter && isFocused) ? 0 : 1 }"></span>
      <slot name="input" :update="updateModel" :isFocused="isFocused">
        <input tabindex="-1" aria-hidden="true" style="display: none;" :name="$attrs.name">
        <input
          ref='input'
          v-bind:type="type"
          v-bind:readonly="readonly"
          v-bind:disabled="disabled"
          v-bind:pattern="pattern"
          v-bind:min="min"
          v-bind:max="max"
          v-bind:step="step"
          v-bind:placeholder="placeholder"
          v-bind:data-hj-allow="dataHjAllow"
          v-bind="customAttrs"
          v-model="internalModelValue"
          @input="processValue"
          @focus="onFocus"
          @blur="onBlur"
          @keyup.enter="updateModel(), $emit('enter')"
          :style="{ opacity: formatter && !isFocused ? 0 : 1 }"
          autocomplete="new-password"
        >
      </slot>
    </div>
    <span class="const postfix" v-if="!vertical && postfix != undefined" v-text="postfix" v-show="!formatter || (formatter && isFocused)"></span>
    <div class="empty" v-if="!vertical"></div>
    <span class="const postpend" v-if="postpend != undefined" v-text="postpend"></span>
  </div>
  <slot name="validation" :message="validationMessages[0]">
    <span class="ui-input-validation-error" v-if="validationMessageShow" v-show="validator" v-text="validationMessages[0]" :class="{ active: validationMessages[0] != undefined, 'keep-space': keepSpace }"></span>
  </slot>
</template>


<style lang="less" scoped>

.ui-input {
  @pad: 10px;
  @h: 40px;

  height: @h;
  padding: @pad;
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

  &.focused { box-shadow: 0 0 0 2px @col-text-dark; }
  &.autoWidth { width: fit-content; }
  .const {
    white-space: nowrap;
    flex: 0 0 0%;
  }
  .empty { flex: 1 1; }
  .prepend { padding-right: 5px; }
  .prefix { padding-right: 2px; }
  .postpend { padding-left: 5px; }
  .postfix { padding-left: 2px; }

  .prepend, .postpend {
    color: @col-text-on-disabled;
    font-size: .85rem;

    @media @mobile { font-size: 0.95rem; }
  }
  .prefix, .postfix, .input-wrapper {
    font-weight: bold;
  }

  .input-wrapper {
    position: relative;
    height: @h;
    overflow: hidden;
    
    span {
      white-space: nowrap;
      overflow: hidden;
      opacity: 0;
      height: @h;
      line-height: @h;

      &.wider { padding-right: 5px; }
    }
    &::v-deep input {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: @h;
      line-height: @h;
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

        &:invalid { min-width: 10px; }
      }
    }
  }

  &.vertical {
    height: auto;
    flex-direction: column;
    align-items: flex-start;

    @media @desktop { padding-bottom: 0; }

    .vertical-container {
      justify-content: flex-start;
      align-items: center;
      max-width: 100%;
    }
    @media @mobile {
      @h: 22px;

      .input-wrapper,
      &::v-deep input {
        height: @h;
        line-height: @h;
      }
      span {
        height: @h;
        line-height: @h;
      }
    }
  }

}

</style>


<script lang="ts">
import { defineComponent } from 'vue';
import { debounce } from 'ts-debounce';


export default defineComponent({

  props: {
    modelValue: { default: '', required: true },
    debounce: { default: 500, type: Number },
    validationMessageShow: { default: false, type: Boolean },
    allowNull: { default: false, type: Boolean },
    keepSpace: { default: false, type: Boolean },
    decimals: { default: 2, type: Number },
    type: String,
    placeholder: String,
    subtype: String,
    prepend: String,
    postpend: String,
    prefix: String,
    dataHjAllow: Boolean,
    postfix: String,
    flexible: Boolean,
    vertical: Boolean,
    formatter: Function,
    validator: Object,
    readonly: { type: [String, Boolean] },
    disabled: { type: [String, Boolean] },
    pattern: String,
    min: Number,
    max: Number,
    step: Number,

    replacers: { default: undefined }
  },
  data() {
    return {
      isFocused: false,
      internalModelValue: '',
      validationMessages: [] as Array<string>,
      customAttrs: {} as Record<string, string>
    }
  },
  watch: {
    modelValue(newVal) {
      if (this.subtype == 'percent') {
        this.internalModelValue = (newVal * 1000 / 10).toString();
        return;
      }
      this.internalModelValue = newVal;
    }
  },
  methods: {
    formatValue(str:any) {
      if (str == undefined || str == '')
        if (this.allowNull)
          return str;
        else
          return '0';

      if (this.formatter && !this.isFocused)
        if (this.subtype == 'percent')
          return this.formatter(str / 100);
        else if (Array.isArray(this.replacers) && str == this.max) {
           if (str == this.max && typeof (<any>this.replacers)[1] == 'string')
            return (<any>this.replacers)[1];
        } else
          return this.formatter(str);

      return str.toString().replaceAll(' ', '.')
    },
    validate() {
      if (this.validator) {
        try {
          this.validator.validateSync(this.internalModelValue);
          this.validationMessages = [];
        } catch (ex) {
          this.validationMessages = [ ex.message ];
        }
      }
    },
    processValue() {
      if (this.validator)
        this.validate();
    },
    updateModel() {
      const validationError = this.validationMessages[0];
      if (validationError)
        setTimeout(() => {
          if (this.validationMessages.includes(validationError))
            this.validationMessages.splice(this.validationMessages.indexOf(validationError), 1);
        }, 1000);

      if (this.type == 'number') {
        if (this.internalModelValue == '' && !this.allowNull)
          this.internalModelValue = <any>(this.min || 0);

        const parsedValue = parseFloat(this.internalModelValue);
        if (this.min != undefined && parsedValue < this.min)
          this.internalModelValue = <any>this.min;

        if (this.max != undefined && parsedValue > this.max)
          this.internalModelValue = <any>this.max;

        if (this.step && this.step > 0) {
          const onGrid = (parsedValue - <number>this.min) / this.step;
          if (!Number.isInteger(onGrid))
            this.internalModelValue = <any>( <number>this.min + Math.round(onGrid) * this.step );
        }
      }

      let value:any = JSON.parse(JSON.stringify(this.internalModelValue));
      if (this.subtype == 'percent')
        value = (<any>value / 100);
      
      if (this.type == 'number')
        if (value != '' || !this.allowNull)
          value = Number(value);

      console.log('updating model with ', value);
      //@ts-ignore
      this.$emit('update:modelValue', value);
    },
    onFocus() {
      if (this.type == 'number') {
        const intVal = this.internalModelValue.toString();
        const dotIndex = intVal.indexOf('.');

        let newVal = Number(Number(this.internalModelValue).toFixed(2));
        if (dotIndex != -1 && intVal.length - dotIndex > 3) {
          //@ts-ignore TODO: refactor types
          this.internalModelValue = this.internalModelValue.indexOf ? newVal.toString() : newVal;
        } else if ((<any>this).prefix == '$') {
          //@ts-ignore TODO: refactor types
          this.internalModelValue = newVal.toFixed(0);
        } else if ((<any>this).postfix == '%') {
          //@ts-ignore TODO: refactor types
          this.internalModelValue = newVal.toFixed(this.decimals);
        }
      }

      this.isFocused = true;
    },
    onBlur() {
      this.isFocused = false;
      this.updateModel();
    },
    focus() {
      this.onFocus();
      (<any>this.$refs.input).focus();
    }
  },
  setup(props, { emit }) {
    // const mapToMinMax = function (value:any) {
    //   if (props.type == 'number') {
    //     if (value == '')
    //       value = (props.min || 0);

    //     if (props.min != undefined && parseFloat(value) < props.min)
    //       value = props.min;

    //     if (props.max != undefined && parseFloat(value) > props.max)
    //       value = props.max;
    //   }
    // };
    // const updateModel = function (internalValue:any) {
    //   mapToMinMax(internalValue);

    //   let value:any = JSON.parse(JSON.stringify(internalValue));
    //   if (props.subtype == 'percent')
    //     value = (<any>value / 100);
      
    //   if (props.type == 'number')
    //     value = Number(value);

    //   //@ts-ignore
    //   emit('update:modelValue', value);
    // };
    // return {
    //   updateModel: debounce(updateModel, props.flexible ? 0 : props.debounce)
    // }
  },
  mounted() {
    if (this.subtype == 'percent')
      this.internalModelValue = (parseFloat(this.modelValue) * 1000 / 10).toString();
    else
      this.internalModelValue = this.modelValue;

    if (this.type == 'number') {
      (<any>this.$refs.input).addEventListener('keydown', function (ev:KeyboardEvent) {
        if (['+', 'e'].includes(ev.key))
          ev.preventDefault();
      });
      this.customAttrs['pattern']='[0-9]*'
      this.customAttrs['inputmode']='numeric'
    }
  }
});
</script>