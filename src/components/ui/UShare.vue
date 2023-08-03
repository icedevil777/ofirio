<template>
  <UDrop mHeader="Share">
    <template v-slot:label>
      <UIcon name="share" />Share
    </template>
    <template v-slot:content>
      <span class="heading hide-mobile">Share</span>
      <div class="share-actions flex">
        <div class="mobile-mm"></div>
        <div class="action">
          <UButton class="ui-btn-circle flex"><UIcon name="external-link" /></UButton>
          Copy link
        </div>
        <div class="action">
          <UButton class="ui-btn-circle flex"><UIcon name="facebook-circle" /></UButton>
          Facebook
        </div>
        <div class="action">
          <UButton class="ui-btn-circle flex"><UIcon name="twitter" /></UButton>
          Twitter
        </div>
        <div class="action">
          <UButton class="ui-btn-circle flex"><UIcon name="gmail" /></UButton>
          Gmail
        </div>
        <div class="action">
          <UButton class="ui-btn-circle flex"><UIcon name="whatsapp" /></UButton>
          What's App
        </div>
        <div class="mobile-mm"></div>
      </div>
    </template>
  </UDrop>
</template>

<style lang="less" scoped>
.share-actions {
  justify-content: space-between;
  align-content: flex-start;
  align-items: flex-start;
  white-space: nowrap;
  
  @media @mobile {
    padding: @mm 0;
    overflow-x: auto;
    width: 100%;
  }
  .action {
    padding-top: 1rem;
    text-align: center;
    color: #777;
    font-size: .75rem;

    @media @mobile {
      padding: 0;
      font-weight: .85rem;
    }
    & + .action {
      margin-left: 1rem;

      @media @mobile { margin-left: @mm; }
    }
    .ui-btn-circle {
      margin: 0 auto .5rem;
      justify-content: center;
      align-items: center;
    }
    .svg-icon {
      @s: 2rem;
      width: @s;
      height: @s;
    }
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';

import UDrop from '@/components/ui/UDrop.vue';
import UButton from '@/components/ui/UButton.vue';

export default defineComponent({
  components: {
    UDrop,
    UButton
  }  
})
</script>