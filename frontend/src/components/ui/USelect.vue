<template>
  <vue-select v-bind="$attrs">
    <template #tag="{ option }">
      <UChip
        name="cross"
        style="margin: 0"
        @onRemove="removeChip(option)"
        v-bind:alt="(option.label || option) + ' Chip'">{{ option.label || option }}</UChip>
    </template>
    <template #toggle="{ isFocusing }">
      <UIcon name="smooth-arrow" :class="{ active: isFocusing }"/>
    </template>
  </vue-select>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import UChip from '@/components/ui/UChip.vue';
import VueSelect from 'vue-next-select';
import 'vue-next-select/dist/index.min.css';

export default defineComponent({
  components: {
    VueSelect,
    UChip
  },
  methods: {
    removeChip(option:any) {
      const $attrs:any = this.$attrs;
      const $refs:any = this.$refs;

      const i = $attrs.modelValue.indexOf(option);
      $attrs.modelValue.splice(i, 1);
    }
  }
});
</script>

<style lang="less" scope>
@h: 45px;

.vue-select {
  width: auto;
  height: @h;
  border: none;
  display: inline-block;

  &.disabled {
    background-color: @col-disabled;
  }

  .svg-icon--smooth-arrow {
    @s: 10px;

    width: @s;
    height: @s;
    margin: 0;
    transform: rotate(180deg);
    transition: transform .3s ease;
    cursor: pointer;

    &.active { transform: rotate(0deg); }
  }
  .vue-select-header {
    height: inherit;
    border-radius: @border-radius;
    border: none;
    box-shadow: 0 0 0 1px @col-gray-light;
    padding: 10px;
    transition: box-shadow ease .15s;

    &:hover { box-shadow: 0 0 0 1px @col-text-dark; }
  }

  &[data-is-focusing="true"] .vue-select-header {
    box-shadow: 0 0 0 2px @col-text-dark;
  }

  .vue-select-header > .icon.loading,
  .vue-select-header > .icon.arrow-downward {
    margin-right: 7px;
  }

  .vue-input {
    height: inherit;
    line-height: @h;
  }

  .vue-input > input {
    height: inherit;
    line-height: inherit;
    font-size: inherit;
  }

  > .vue-input {
    position: absolute;
    top: 1px;
    height: @h - 2px;
    width: 100%;
    padding: 0 10px;
    
  }

  .vue-select-header > .vue-input > input[disabled] {
    color: @col-text-on-disabled;
  }

  .vue-input > input[readonly],
  .vue-input > input[disabled] {
    background-color: unset;

    &::placeholder {
      font-weight: 600;
      color: @col-text-dark;
      opacity: 1;
    }
  }

  .vue-dropdown {
    max-height: 300px;
    width: calc(100% - 30px);
    left: -5px;
    padding: 20px;
    border: none;
    border-radius: @border-radius;
    box-shadow: @shadow @col-shadow;
  }
  &.direction-bottom .vue-dropdown { top: @h + 10px !important; }
  &.direction-top .vue-dropdown { bottom: @h + 10px !important; }
  

  .vue-dropdown-item {
    padding: 8px 0;
    background: transparent !important;
    font-size: inherit;
  }

  .vue-dropdown-item.highlighted {
    color: @col-blue;
  }

  .vue-dropdown-item.disabled {
    color: @col-gray;
    cursor: not-allowed;
  }

  .vue-dropdown-item.selected {
    font-weight: bold;
    color: @col-blue;
  }


  .vue-tags {
    display: flex;
    flex-wrap: wrap;
    margin: 0;
    padding: 2px;
    min-height: calc(1rem + 4px);
    user-select: none;
  }

  .vue-tag, .vue-tag.selected {
    border-radius: 0;
    background-color: transparent;
    padding: 0;
    margin: 2px;
  }


}

</style>