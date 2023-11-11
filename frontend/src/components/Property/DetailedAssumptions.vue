<template>
  <PropBasicAssumptionWrapper class="detailed-assumptions">
    <UIcon name="pencil" @click="() => customizationPopup ? customizationPopup.open() : undefined" />
    <span class="heading hide-mobile">Detailed Assumptions</span>
    <span class="heading hide-desktop">Assumptions</span>
    <table class="fin-table">
      <tr>
        <td class="title title-bigger" colspan="3">Price And Market Related</td>
      </tr>
      <tr>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['annual_increase_in_rent']"/> Annual Increase In Rent</td>
        <td v-if="Account.Basis.isPremium" class="value">{{ $format['%'](financeModel.dto?.detailed.annual_increase_rent) }}</td>
        <td v-if="!Account.Basis.isPremium" class="hidden" rowspan="3"><UnlockAnalytics>{{ $isMobile.value ? 'Unlock' : 'Unlock Analytics' }}</UnlockAnalytics></td>
      </tr>
      <tr>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['annual_increase_in_property_value']"/> Annual Increase In Property Value</td>
        <td v-if="Account.Basis.isPremium" class="value">{{ $format['%'](financeModel.dto?.detailed.annual_increase_prop) }}</td>
      </tr>
      <tr>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['general_inflation']"/> General Inflation</td>
        <td v-if="Account.Basis.isPremium" class="value">{{ $format['%'](financeModel.dto?.detailed.general_inflation) }}</td>
      </tr>
      <tr>
        <td class="title title-bigger" colspan="3">Property Related</td>
      </tr>
      <tr>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['average_length_of_tenant_stay']"/> Average Length Of Tenant Stay</td>
        <td v-if="Account.Basis.isPremium" class="value">{{ $format['number'](financeModel.dto?.detailed.average_length_stay_years) }}</td>
        <td v-if="Account.Basis.isPremium" class="unit">years</td>
        <td v-if="!Account.Basis.isPremium" class="hidden" rowspan="6"><UnlockAnalytics>{{ $isMobile.value ? 'Unlock' : 'Unlock Analytics' }}</UnlockAnalytics></td>
      </tr>
      <tr>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['management_fees']"/> Management Fees</td>
        <td v-if="Account.Basis.isPremium" class="value">{{ $format['%'](financeModel.dto?.detailed.management_fees_percent) }}</td>
        <td v-if="Account.Basis.isPremium" class="unit">of gross rent</td>
      </tr>
      <tr>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['maintenance_reserves']"/> Maintenance / Reserves</td>
        <td v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](financeModel.dto?.detailed.maintenance_cost_amount) }}</td>
        <td v-if="Account.Basis.isPremium" class="unit"></td>
      </tr>
      <tr>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['overhead_miscellanous']"/> Overhead / Miscellanous</td>
        <td v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](financeModel.dto?.detailed.overhead_cost_amount) }}</td>
        <td v-if="Account.Basis.isPremium" class="unit"></td>
      </tr>
      <tr>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['closing_costs_on_purchase']"/> Closing Costs On Purchase</td>
        <td v-if="Account.Basis.isPremium" class="value">{{ $format['%'](financeModel.dto?.detailed.closing_cost_on_purchase_percent) }}</td>
        <td v-if="Account.Basis.isPremium" class="unit">of property purhase price</td>
      </tr>
      <tr>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['closing_costs_on_sale']"/> Closing Costs On Sale</td>
        <td v-if="Account.Basis.isPremium" class="value">{{ $format['%'](financeModel.dto?.detailed.closing_cost_on_sale_percent) }}</td>
        <td v-if="Account.Basis.isPremium" class="unit">of property sales price</td>
      </tr>
    </table>
  </PropBasicAssumptionWrapper>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

import UTooltip from '@/components/ui/UTooltip.vue';
import PropBasicAssumptionWrapper from '@/components/Property/PropBasicAssumptionWrapper.vue';
import TooltipTexts from '@/constants/Tooltips';
import UnlockAnalytics from '@/components/OFRC/UnlockAnalytics.vue';
import AccountStore from '@/models/Account';

export default defineComponent({
  components: {
    UTooltip,
    PropBasicAssumptionWrapper,
    UnlockAnalytics
  },
  props: {
    customizationPopup: Object,
    financeModel: { type: Object, required: true }
  },
  computed: {
    TooltipTexts() {
      return TooltipTexts;
    },
    Account() {
      return AccountStore;
    }
  }
})
</script>

<style lang="less" scoped>
.detailed-assumptions {
  background: #f9f9f9;
  
  > span.heading { margin-bottom: 0; }
  > .fin-table {
    > tr > td.title { padding-top: 30px; }

    .hidden {
      position: relative;
      width: 180px;

      .unlock-analytics {
        position: absolute;
        width: 100%;
        height: 100%;
      }
      @media @mobile { width: 80px; }
    }
  }

  @media @mobile {
    > .fin-table {
      tr td:nth-child(3) { display: none; }
    }
  }
}
</style>