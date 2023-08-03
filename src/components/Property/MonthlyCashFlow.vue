<template>
  <PropBasicAssumptionWrapper class="monthly-cash-flow">
    <UIcon name="pencil" @click="() => customizationPopup ? customizationPopup.open() : undefined" />
    <span class="heading">Monthly Cash Flow (Year 1)</span>
    <table class="fin-table">
      <tr class="hide-desktop">
        <td></td>
        <td class="title" colspan="2">Income</td>
      </tr>
      <tr>
        <td class="title">Income</td>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['rent']"/> Rent (After Vacancy)</td>
        <td v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](financeModel.dto?.monthly_cash_flow.month_rent_less_vacancy) }}</td>
        <td v-if="!Account.Basis.isPremium" class="hidden" rowspan="14"><UnlockAnalytics>{{ $isMobile.value ? 'Unlock' : 'Unlock Analytics' }}</UnlockAnalytics></td>
      </tr>
      <tr class="divider stripped">
        <td colspan="3"></td>
      </tr>
      <tr class="hide-desktop">
        <td></td>
        <td class="title" colspan="2">Expenses</td>
      </tr>
      <tr>
        <td class="title">Expenses</td>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['management_fees']"/> Management Fees</td>
        <td v-if="Account.Basis.isPremium" class="value">-{{ $format['usdInt'](financeModel.dto?.monthly_cash_flow.month_management_fees) }}</td>
      </tr>
      <tr>
        <td class="title"></td>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['maintenance_reserves']"/> Maintenance / Reserves</td>
        <td v-if="Account.Basis.isPremium" class="value">-{{ $format['usdInt'](financeModel.dto?.monthly_cash_flow.month_maintenance_reserves) }}</td>
      </tr>
      <tr>
        <td class="title"></td>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['hqa_fees']"/> HOA Fees</td>
        <td v-if="Account.Basis.isPremium" class="value">-{{ $format['usdInt'](financeModel.dto?.monthly_cash_flow.month_hoa_fees) }}</td>
      </tr>
      <tr>
        <td class="title"></td>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['insurance']"/> Insurance</td>
        <td v-if="Account.Basis.isPremium" class="value">-{{ $format['usdInt'](financeModel.dto?.monthly_cash_flow.month_insurance) }}</td>
      </tr>
      <tr>
        <td class="title"></td>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['property_taxes']"/> Property Taxes</td>
        <td v-if="Account.Basis.isPremium" class="value">-{{ $format['usdInt'](financeModel.dto?.monthly_cash_flow.month_property_taxes) }}</td>
      </tr>
      <tr>
        <td class="title"></td>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['agent_leasing_fees']"/> Agent Leasing Fees</td>
        <td v-if="Account.Basis.isPremium" class="value">-{{ $format['usdInt'](financeModel.dto?.monthly_cash_flow.month_re_lease_fees) }}</td>
      </tr>
      <tr>
        <td class="title"></td>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['overhead_miscellanous']"/> Overhead / Miscellanous</td>
        <td v-if="Account.Basis.isPremium" class="value">-{{ $format['usdInt'](financeModel.dto?.monthly_cash_flow.month_overhead_miscellanous) }}</td>
      </tr>
      <tr class="divider solid">
        <td colspan="3"></td>
      </tr>
      <tr>
        <td class="title"></td>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['operating_income']"/> Operating Income</td>
        <td v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](financeModel.dto?.monthly_cash_flow.month_operating_income) }}</td>
      </tr>
      <tr>
        <td class="title"></td>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['loan_payments']"/> Loan Payments</td>
        <td v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](financeModel.dto?.monthly_cash_flow.month_loan_payments) }}</td>
      </tr>
      <tr>
        <td class="title"></td>
        <td class="name"><UTooltip mode="top" :text="TooltipTexts['net_income']"/> Net Income</td>
        <td v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](financeModel.dto?.monthly_cash_flow.net_income) }}</td>
      </tr>
      <tr>
        <td class="title"></td>
        <td class="name ui-text-bold"><UTooltip mode="top" :text="TooltipTexts['cash_flow']"/> Cash Flow</td>
        <td v-if="Account.Basis.isPremium" class="value" v-colorBy:posNeg="financeModel.dto?.monthly_cash_flow.month_cash_income_loss">{{ $format['usdInt'](financeModel.dto?.monthly_cash_flow.month_cash_income_loss) }}</td>
      </tr>
    </table>
  </PropBasicAssumptionWrapper>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

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
.monthly-cash-flow {
  background: #e6faf4;

  > .fin-table {
    tr > td.ui-text-bold { color: @col-text-dark; }

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
   
    @media @mobile { tr td:first-child { display: none; } }
  }
}
</style>