<template>
  <span v-if="label == 'new'" class="new label">New</span>
  <span v-else-if="label == 'good_deal'" class="good-deal label">Good Deal</span>
  <span v-else-if="label == 'sold'" class="sold label">Sold</span>
  <span v-else-if="label == 'pending'" class="sold label">Pending</span>
  <span v-else-if="label == 'for_sale'" class="for-sale label">For Sale</span>
  <span v-else-if="label == 'recommended'" class="recommended label">Recommended</span>
  <span v-else-if="label == '55plus'" class="fifty-five-plus label">55+</span>
  <span v-else-if="label == 'cash_only'" class="cash_only label">Cash Only</span>
  <span v-else-if="label == 'rehab'" class="rehab-opportunity label">Rehab {{ !$isMobile.value ? 'Opportunity' : '' }}</span>
</template>
<style lang="less" scoped>
  .label {
    font-size: 0.625rem;
    font-weight: 800;
    text-transform: uppercase;
    height: fit-content;
    padding: 4px 8px;
    border-radius: 3px;

    @media @mobile { font-size: 0.8rem; }
  }
  .new { background: @col-bg; }
  .good-deal {
    color: @col-text-light;
    background: @col-success;
  }
  .sold {
    color: @col-text-light;
    background: @col-err;
  }
  .for-sale {
    color: @col-text-on-disabled;
    background: @col-disabled;
  }
  .recommended {
    color: @col-text-light;
    background: @col-blue;
  }
  .fifty-five-plus { background: #FFE2B6; }
  .rehab-opportunity { background: #F9EDE0; }
  .cash_only { background: #e7ffdf; }
</style>
<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  props: {
    label: String
  }
});
</script>