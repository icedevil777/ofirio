<template>
  <div class="ui-small-prop">
    <slot name="value" :value="value" :styles="colorDefine">
      <span
        class="value"
        v-text="displayValue"
        :style="colorDefine"
      ></span>
    </slot>
    <slot name="label" :label="label">
      <span class="label" v-text="label"></span>
    </slot>
  </div>
</template>

<style lang="less" scoped>
.ui-small-prop {
  font-weight: 700;

  &::v-deep {
    > span {
      display: block;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    > .value {
      font-size: 1.25rem;
      margin-bottom: 5px;

      @media @mobile { font-size: 1.125rem; }
    }
    > .label {
      color: @col-text-gray-darker;
      text-transform: uppercase;
      font-size: .75rem;

      // @media @mobile { font-size: .75rem; }
    }
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';
import { colorSchemePipeStyle } from '@/pipes/ColorSchemes.pipe';

export default defineComponent({
  props: {
    label: { type: String, required: true },
    value: { required: true },
    prefix: { type: String, default: '' },
    postfix: { type: String, default: '' },
    colorScheme: String,
    formatter: Function
  },
  computed: {
    colorDefine():{ color?: string } {
      return colorSchemePipeStyle(<string>this.colorScheme, <number>this.value);
    },
    displayValue():string {
      return this.prefix + '' + ( this.formatter ? this.formatter(this.value) : this.value) + '' + this.postfix;
    }
  }
})
</script>