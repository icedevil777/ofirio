<template>
  <div class="flex password-strength">
    <span :class="{
      good: !validationResult.includes('all') && !validationResult.includes('Minimal length is 6')
    }">6 to 20 characters</span>
    <span :class="{
      good: !validationResult.includes('all') && !validationResult.includes('Minimal 1 digit')
    }">Min 1 digit</span>
    <span :class="{
      good: !validationResult.includes('all') && !validationResult.includes('Minimal 1 character')
    }">Min 1 letter</span>
  </div>
</template>

<style lang="less" scoped>
  .password-strength {
    flex-wrap: wrap;
    justify-content: flex-start;
    align-content: flex-start;
    align-items: flex-start;

    > span {
      @h: .875rem;

      display: flex !important;
      justify-items: flex-start;
      align-items: center;
      align-content: center;
      margin-top: 10px;
      margin-left: 10px;
      color: @col-text-gray-darker;
      font-size: @h;

      &:before {
        @s: 6px;
        content: '';

        width: @s;
        height: @s;
        display: inline-block;
        margin-right: 7px;
        border-radius: 50%;
        background: @col-gray;
      }
      &.good {
        &:before { background: @col-green; }
      }
    }
  }
</style>

<script lang="ts">
import { defineComponent } from 'vue';
import { VPassword } from '@/models/yups.model';

export default defineComponent({
  props: {
    passmodel: { types: [ null, String ], required: true }
  },
  computed: {
    validationResult() {
      if (this.passmodel == null || this.passmodel == undefined)
        return [ 'all' ];
      try { VPassword.validateSync(this.passmodel, { abortEarly: false }); }
      catch (ex) { return ex.errors; }
      return [];
    }
  }
})
</script>