<template>
  <div class="ui-chip" v-bind="$attrs">
    <slot></slot>
    <UIcon name="cross" @click.prevent.stop="emitRemove"/>
  </div>  
</template>

<style lang="less" scoped>
.ui-chip {
  @h: 30px;

  display: inline-block;
  margin: 0 5px;
  height: @h;
  border-radius: @h/2;
  padding: 0 12px;
  line-height: @h;
  white-space: nowrap;
  background: @col-blue;
  color: @col-text-light;
  font-weight: bold;
  font-size: 0.875rem;

  .svg-icon--cross {
    vertical-align: middle;
    @s: 12px;
    fill: @col-text-light;
    cursor: pointer;
    width: @s;
    height: @h;
    margin-left: @s/2;
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  methods: {
    emitRemove(event:MouseEvent) {
      this.$emit('onRemove', event);
    }
  }
})
</script>