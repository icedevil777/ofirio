<template>
  <transition-group name="sliding" tag="div" class="ui-message-list">
    <UMessage
      v-for="msg of list"
      :key="msg"
      :type="msg.message.type"
      :text="msg.message.message"
      class="ui-message-inList"
      @remove="() => remove(msg)"
    />
  </transition-group>
</template>

<style lang="less" scoped>
.ui-message-list {
  .ui-message {
    will-change: margin-top, max-height;
    transition: opacity .2s linear, max-height .3s ease, visibility .3s ease;

    & + & { margin-top: 10px }
    &:last-child { margin-bottom: 1rem; }
  }
  .sliding-enter-from,
  .sliding-leave-to {
      opacity: 0;
      max-height: 0;
      visibility: hidden;
      margin: 0;
  }

}
</style>

<script lang="ts">
import { defineComponent } from 'vue';
import UMessage from './UMessage.vue';

export default defineComponent({
  components: {
    UMessage
  },
  props: {
    initialList: { required: false, type: Array },
    initialDelay: Number,
    maxCount: Number
  },
  data() {
    return {
      list: [] as Array<any>
    }
  },
  methods: {
    push(message:any, timeout = 5000) {
      const newMessage = {
        message,
        visible: false
      };

      this.list.push(newMessage);
      if (this.maxCount && this.list.length > this.maxCount)
        this.remove(this.list[0]);
        
      if (timeout != 0)
        setTimeout(() => { this.remove(newMessage); }, timeout);
    },
    remove(messageObject: any) {
      const i = this.list.indexOf(messageObject);
      if (i === -1)
        return;

      this.list.splice(i, 1);
    },
    reset(hard: boolean) {
      this.list = [];
    }
  },
  mounted() {
    if (this.initialList)
      for (let msg of this.initialList)
        this.push(msg, this.initialDelay);
  }
})
</script>