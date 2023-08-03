/**
 * @usage:
 *
 *   <UTextInput value="value_name" name="input_name" v-model="model">Label</UTextInput>
 *
 */

<template>
  <div class="ui-input-textarea" v-bind:class="{ focused: isFocused, autoWidth: flexible }" @click="$refs.input.focus()">
    <textarea
      ref='input'
      v-bind="$attrs"
      :value = "modelValue"
      @input="updateModel"
      @focus="isFocused = !0"
      @blur="isFocused = !1"
    ></textarea>
  </div>
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

  &.focused { box-shadow: 0 0 0 2px @col-blue; }
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

}

</style>


<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({

  props: {
    modelValue: { default: '', required: true },
    flexible: Boolean
  },
  data() {
    return {
      isFocused: false
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