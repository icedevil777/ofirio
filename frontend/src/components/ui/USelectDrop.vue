<template>
  <UDrop class="ui-select-drop" :mHeader="mHeader" :disabled="disabled">
    <template v-slot:label>
      <span class="label" v-text="label"></span>
      <UIcon name="smooth-arrow" />
    </template>
    <template v-slot:content="{ props }">
      <slot name="content" :props="props" :select="select">
        <div class="flex" v-for="o of options" :key="o" :class="{ active: o == modelValue }" @click="select(o), props.close()">
          <slot name="item" :option="o"></slot>
        </div>
      </slot>
    </template>
  </UDrop>
</template>


<style lang="less" scoped>
.ui-select-drop {
  color: @col-text-gray-darker;
  
  &::v-deep {
    .ui-drop-container {
      padding: 12px 0;
      width: 100%;
      z-index: 10;

      @media @mobile { padding: 0; }
      > .flex,
      > .scroll-container > .flex {
        justify-content: flex-start;
        align-items: center;
        white-space: nowrap;
        color: @col-text-dark;
        cursor: pointer;
        font-size: .9375rem;
        padding: 0 20px;
        line-height: 40px;
        height: 40px;

        &:hover { background: @col-disabled; }
        &.active {
          font-weight: 700;
          color: @col-blue;
        }
        .svg-icon {
          @s: 20px;

          width: @s;
          height: @s;
          margin-right: 12px;
        }
      }
      .ui-drop-mHeader { color: @col-text-dark; }
    }
    .ui-drop-label {
      box-shadow: 0 0 0 1px @col-gray-light;
      padding: 0 15px;
      height: 45px;
      line-height: 45px;
      color: @col-text-dark;
      background: transparent;
      width: 100%;

      > .label { flex: 1; }
    }
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';
import UDrop from '@/components/ui/UDrop.vue';

export default defineComponent({
  components: {
    UDrop
  },
  props: {
    options: { required: true, type: Array },
    modelValue: { required: true, default: '' },
    label: { required: true, default: '' },
    disabled: { default: false, type: Boolean },
    mHeader: String
  },
  methods: {
    select(o: any) {
      this.$emit('update:modelValue', o);
    }
  }
})
</script>