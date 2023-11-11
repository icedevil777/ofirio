<template>
  <label class="ui-radio-chip" :class="{ selected: isChecked }">
    <input
      type="radio"
      v-bind="$attrs"
      :checked="isChecked"
      @change="updateModel"
    ><slot></slot>
  </label>
</template>

<style lang="less" scoped>

.ui-radio-chip {
  @pad: 12px;
  @h: 30px;

  height: @h;
  line-height: @h;
  padding: 0 @pad;
  box-shadow: 0 0 0 1px @col-gray;
  border-radius: @h/2;
  color: @col-text-gray-dark;
  position: relative;
  display: inline-block;
  font-weight: 600;
  text-align: center;
  min-width: 60px;
  font-size: 0.75rem;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color .1s ease, color .3s ease, box-shadow .3s ease;

  &:hover, &:focus {
    box-shadow: 0 0 0 1px @col-blue;
  }
  &.selected {
    background: @col-blue;
    box-shadow: 0 0 0 1px @col-blue;
    color: @col-bg;
  }
  & + .ui-radio-chip { margin-left: 10px; }
  input {
    position: absolute;
    width: 0;
    height: 0;
    opacity: 0;
  }
}

</style>


<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({

  computed: {
    isChecked():Boolean {
      return this.modelValue == this.$attrs.value;
    }
  },

  props: {
    modelValue: { default: '', required: true }
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