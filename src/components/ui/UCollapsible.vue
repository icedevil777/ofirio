/**
 * @usage:
 *
 *   <UTextInput value="value_name" name="input_name" v-model="model">Label</UTextInput>
 *
 */

<template>
  <div class="ui-collapsible" v-bind:class="{ opened: isOpen }" v-bind:tabIndex="isOpen ? 0 : -1">
    <div class="header" @click="toggle()">
      <slot name="header" :isOpen="isOpen">
        <div class="flex">
          <span class="label" v-text="label"></span>
          <UIcon name="smooth-arrow"/>
        </div>
      </slot>
    </div>
    <transition
      name="expand"
      @before-enter="setState('opening')"
      @after-enter="setState('opened')"

      @leave="setState('closing')"
      @after-leave="setState('closed')"
    >
      <div class="container" ref="container" v-show="isOpen" :style="maxHeightComputer"><slot :isOpen="isOpen" name="default"></slot></div>
    </transition>
  </div>
</template>


<style lang="less" scoped>
.ui-collapsible {
  outline: none;
  
  .header .flex {
    @h: 40px;

    justify-content: space-between;
    align-items: center;
    height: @h;
    font-weight: bold;
    font-size: 1rem;
    cursor: pointer;

    &:deep(.svg-icon) {
      width: @h/2;
      height: @h/2;
      transform: rotate(180deg);
      transition: transform ease .2s;
    }
  }
  > .container {
    opacity: 0;
    max-height: 0;
    overflow: hidden;

    &.expand-leave-active, &.expand-enter-active {
      transition: opacity ease .2s, max-height ease .3s;
    }
  }
  &.opened {
    > .container { opacity: 1; }
    .header:deep(.svg-icon) {
      transform: rotate(0) !important;
    }
  }
}
</style>


<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  props: {
    label: String,
    opened: { type: Boolean, default: false }
  },
  data() {
    return {
      maxHeight: 0,
      isOpen: false,
      state: 'closed' as string
    }
  },
  computed: {
    maxHeightComputer():object {
      if (this.state == 'closed' || this.state == 'closing')
        return { 'max-height': '0' };

      if (this.state == 'opened')
        return { 'max-height': 'none', 'overflow': 'visible' };
      
      return { 'max-height': this.getScrollHeight() + 'px', 'display': 'block' };
    }
  },
  methods: {
    getScrollHeight() {
      const el = this.$refs.container as HTMLDivElement;
      return el.scrollHeight;
    },
    toggle(forceState: boolean) {
      const toState = forceState == undefined ? !this.isOpen : forceState;

      if (!toState)
        this.state = 'beforeclosing';
      
      this.isOpen = toState;
    },
    setState(state: string) { this.state = state; }
  },
  mounted() {
    if (this.opened) {
      this.isOpen = true;
      this.maxHeight = this.getScrollHeight();
    }
  }
});
</script>