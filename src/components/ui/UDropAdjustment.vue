<template>
<div class="ui-drop-adjustment">
  <slot></slot>
  <div class="controls flex">
    <UButton class="ui-btn-text-gray" @click="$emit('reset')">Reset</UButton>
    <UButton class="ui-btn ui-btn-green" @click="$emit('apply')">Apply</UButton>
  </div>
</div>
</template>

<style lang="less" scoped>
.ui-drop-adjustment {
  .controls {
    width: 100%;
    margin-top: 20px;
    justify-content: space-between;

    @media @mobile {
      padding: 10px 20px;
      border-top: 1px solid @col-gray;
    }

    .ui-btn-text-gray {
      text-decoration: underline;

      @media @mobile {
        position: absolute;
        top: 18px;
        left: 20px;
        font-size: 1rem;
        padding: 0;
        text-decoration: none;
      }
    }
    .ui-btn {
      padding: .5rem 2rem;

      @media @mobile { width: 100%; }
    }
  }
}
.ui-drop-adjustment::v-deep {
  span { display: block; }
  span.drop-title {
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 10px;
  }
  span.name { margin-bottom: 10px; }
  .ui-input { margin: 10px 0 20px; }
  .ui-input + .ui-input-validation-error { margin-top: -5px; }
  .ui-input + .ui-input-validation-error.active { margin-top: -10px; margin-bottom: 20px; }

  .ui-slider {
    margin: 20px 0;
    width: 100%;
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';
import UButton from '@/components/ui/UButton.vue';

export default defineComponent({
  components: {
    UButton
  },
  methods: {}
})
</script>