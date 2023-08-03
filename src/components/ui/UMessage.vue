<template>
  <div class="ui-message flex" v-bind:class="{
    'ui-message--error': type == 'error',
    'ui-message--warning': type == 'warning',
    'ui-message--success': type == 'success',
    'ui-message--info': type == 'info',
    'ui-message--custom-rent-anal-limit-warning': type == 'custom-rent-anal-limit-warning',
  }">
    <UIcon :name="iconName" />
    <span class="message-text"><slot>{{ text }}</slot></span>
    <UIcon name="cross" @click="emitClose" v-if="!noClose" />
  </div>
</template>

<style lang="less" scoped>
.ui-message {
  @h: 40px;

  border-radius: 5px;
  color: @col-text-light;
  height: @h;
  max-height: @h;
  justify-content: space-between;
  align-content: center;
  align-items: center;
  padding: 0 1rem;
  background: @col-text-gray-darker;
  margin-bottom: 10px;

  &.ui-message--error { background: @col-err; }
  &.ui-message--warning { background: @col-warn; }
  &.ui-message--success { background: @col-success; }
  &.ui-message--info { background: @col-text-gray-dark; }
  &.ui-message--custom-rent-anal-limit-warning {
    background: #efeef9;
    color: @col-text-dark;
  }

  .svg-icon {
    @s: 1rem;

    width: @s;
    min-width: @s;
    height: @s;
    min-height: @s;
    fill: @col-text-light;
  }
  .message-text {
    flex: 1;
    padding: 0 .5rem;
    font-weight: 600;
    font-size: 0.875rem;
  }
  .svg-icon--cross {
    @s: .75rem;

    cursor: pointer;
    width: @s;
    min-width: @s;
    height: @s;
    min-height: @s;
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';

const iconList = <Record<string, string>>{
  'error': 'cross-circle',
  'warning': 'info-circle',
  'success': 'checked-circle',
  'info': 'info-circle',
  'custom-rent-anal-limit-warning': 'triangle-warning-color',
}

export default defineComponent({
  props: {
    text: { type: String },
    type: { default: 'info', type: String },
    noClose: { default: false, type: Boolean }
  },
  setup(attrs) {
    return {
      iconName: iconList[attrs.type] ? iconList[attrs.type] : iconList['info']
    }
  },
  methods: {
    emitClose() {
      this.$emit('remove');
    }
  }
})
</script>