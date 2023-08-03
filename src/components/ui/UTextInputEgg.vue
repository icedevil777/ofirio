/**
 * @usage:
 *
 *   <UTextInput value="value_name" name="input_name" v-model="model">Label</UTextInput>
 *
 */

<template>
  <div class="ui-input flex" :class="{ focused: isFocused, flexible, vertical, invalid: egg.dirty && !isFocused  && egg.invalid }" @click="focus">
    <span class="prepend" v-if="prepend != undefined" v-text="prepend"></span>
    <div class="slayer slayer-first" v-if="alignInput == 'center' || alignInput == 'right'"></div>
    <div class="inputable flex">
      <span class="prefix" v-if="prefix" v-text="prefix"></span>
      <div class="input-wrapper" :class="{ flexible }" :data-value="internalValue">
        <input tabindex="-1" aria-hidden="true" style="visibility: hidden; position: absolute; top:0; left: 0;" :name="name" v-if="!name.startsWith('input__')">
        <input
          size="1"

          :type="type || 'text'"
          :name="name"
          :readonly="egg.readonly || readonly"
          :disabled="egg.disabled || disabled"
          :step="step"
          :placeholder="placeholder"

          @focus="onFocus"
          @blur="onBlur"
          @input="onInput"

          v-model="internalValue"
          v-bind="appendAttributes"
          ref="input"
        >
      </div>
      <span class="postfix" v-if="postfix" v-text="postfix"></span>
    </div>
    <div class="slayer slayer-last" v-if="alignInput == 'center' || alignInput == 'left'"></div>
    <span class="postpend" v-if="postpend != undefined" v-text="postpend"></span>
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
  transition: box-shadow ease-out .2s;
  justify-content: flex-start;
  align-content: center;
  align-items: center;

  &.focused { box-shadow: 0 0 0 2px @col-text-dark; }
  &.invalid { box-shadow: 0 0 0 1.5px @col-err; }
  &.flexible {
    width: fit-content;

    .slayer {
      display: block;
      flex: 1 1;
    }
    .inputable { flex: 0 1 100%; }
  }
  &.vertical {
    flex-direction: column;
    height: auto;

    .prepend, .postpend {
      width: 100%;
      padding: 0;
    }
    .prepend { padding-bottom: 10px; }
    .postpend { padding-top: 10px; }
    .inputable { width: 100%; }
  }

  .slayer { display: none; }

  .prefix, .postfix, .prepend, .postpend {
    white-space: nowrap;
    flex: 0 0 0%;
  }

  .prepend { padding-right: 5px; }
  .postpend { padding-left: 5px; }
  .prepend, .postpend {
    color: @col-text-gray-dark;
    font-size: .8rem;

    @media @mobile { font-size: 0.95rem; }
  }

  .prefix { padding-right: 2px; }
  .postfix { padding-left: 2px; }
  .prefix, .postfix {
    font-weight: bold;
  }

  .inputable {
    justify-content: flex-start;
    align-items: stretch;
    align-content: center;
    flex: 1;

    .input-wrapper {
      font-weight: bold;
      width: 100%;
      position: relative;

      &.flexible {
        display: inline-grid;
        vertical-align: top;
        align-items: center;
        width: auto;
      }

      .prefix, .postfix, &:after, input { font: inherit; }
      &:after,
      input {
        width: auto;
        min-width: 3px;
        max-width: 100%;
        grid-area: ~"1/2";
        margin: 0;
        background: none;
        border: none;
        padding: 0;
      }
      input {
        appearance: none;
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        width: 100%;

        &:focus {
          border: 0;
          outline: none !important;
        }
        &::placeholder { font-weight: 500; }
      }
      &.flexible:after {
        content: attr(data-value);
        visibility: hidden;
        white-space: pre;
        overflow: hidden;
        padding-right: 1px;
      }
    }
  }
}

</style>


<script lang="ts">
import { defineComponent } from 'vue';
import { EggInputModel } from '@/models/Henhouse/Egg.mixin';

export default defineComponent({
  mixins: [EggInputModel],
  props: {
    step: Number,
    type: String,

    prepend: String,
    postpend: String,

    prefix: String,
    postfix: String,

    alignInput: { default: 'left', type: String },
    vertical: Boolean
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
});
</script>