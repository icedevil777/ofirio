<template>
  <PropBasicAssumptionWrapper class="perfomance-dashboard">
    <UIcon name="pencil" @click="() => customizationPopup ? customizationPopup.open() : undefined" />
    <span class="heading">Perfomance Dashboard</span>
    <div class="flex">
      <div class="side">
        <table class="fin-table">
          <tr>
            <td class="title" colspan="2">Investment </td>
          </tr>
          <tr>
            <td class="name"><UTooltip mode="top" :text="TooltipTexts['down_payment']"/> Down Payment / Equity Investment</td>
            <td v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](financeModel.dto?.performance.equity_investment) }}</td>
            <td v-if="!Account.Basis.isPremium" class="hidden" rowspan="4"><UnlockAnalytics>{{ $isMobile.value ? 'Unlock' : 'Unlock Analytics' }}</UnlockAnalytics></td>
          </tr>
          <tr>
            <td class="name"><UTooltip mode="top" :text="TooltipTexts['loan_value']"/> Loan Value, Incl. Closing Costs</td>
            <td v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](financeModel.dto?.performance.loan_value) }}</td>
          </tr>
          <tr class="divider solid">
            <td colspan="2"></td>
          </tr>
          <tr>
            <td class="name"><UTooltip mode="top" :text="TooltipTexts['total_investment']"/> Total Investment (Assets)</td>
            <td v-if="Account.Basis.isPremium" class="value total">{{ $format['usdInt'](financeModel.dto?.performance.total_investment) }}</td>
          </tr>
        </table>
        <table class="fin-table">
          <tr>
            <td class="title" colspan="3">Income</td>
          </tr>
          <tr>
            <td class="name"><UTooltip mode="top" :text="TooltipTexts['operating_income']"/> Operating Income (Year 1)</td>
            <td v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](financeModel.dto?.performance.operating_income_year1) }}</td>
            <td v-if="!Account.Basis.isPremium" class="hidden" rowspan="3"><UnlockAnalytics>{{ $isMobile.value ? 'Unlock' : 'Unlock Analytics' }}</UnlockAnalytics></td>
          </tr>
          <tr>
            <td class="name"><UTooltip mode="top" :text="TooltipTexts['net_income']"/> Net Income (Year 1)</td>
            <td v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](financeModel.dto?.performance.net_income_year1) }}</td>
          </tr>
          <tr>
            <td class="name"><UTooltip mode="top" :text="TooltipTexts['cash_flow']"/> Cash Flow (Year 1)</td>
            <td v-if="Account.Basis.isPremium" class="value" v-colorBy:posNeg="financeModel.dto?.performance.cash_flow_year1">{{ $format['usdInt'](financeModel.dto?.performance.cash_flow_year1) }}</td>
          </tr>
        </table>
      </div>
      <div class="side">
        <table class="fin-table">
          <tr>
            <td class="title" colspan="2">Basic Indicators</td>
          </tr>
          <tr>
            <td class="name"><UTooltip mode="top" :text="TooltipTexts['cap_rate']"/> Cap Rate (Year 1)</td>
            <td v-if="Account.Basis.isPremium" class="value" v-colorBy:cap-coc="financeModel.dto?.performance.cap_rate_year1">{{ $format['%'](financeModel.dto?.performance.cap_rate_year1) }}</td>
            <td v-if="!Account.Basis.isPremium" class="hidden" rowspan="4"><UnlockAnalytics>{{ $isMobile.value ? 'Unlock' : 'Unlock Analytics' }}</UnlockAnalytics></td>
          </tr>
          <tr>
            <td class="name"><UTooltip mode="top" :text="TooltipTexts['cash_on_cash']"/> Cash On Cash (Year 1)</td>
            <td v-if="Account.Basis.isPremium" class="value" v-colorBy:cap-coc="financeModel.dto?.performance.cash_on_cash_year1">{{ $format['%'](financeModel.dto?.performance.cash_on_cash_year1) }}</td>
          </tr>
          <tr>
            <td class="name"><UTooltip mode="top" :text="TooltipTexts['one_perc_rule']"/> 1% Rule</td>
            <td v-if="Account.Basis.isPremium" class="value">{{ $format['%'](financeModel.dto?.performance.one_percent_rule) }}</td>
          </tr>
          <tr>
            <td class="name"><UTooltip mode="top" :text="TooltipTexts['gross_yield']"/> Gross Yield (Year 1)</td>
            <td v-if="Account.Basis.isPremium" class="value">{{ $format['%'](financeModel.dto?.performance.gross_yield) }}</td>
          </tr>
        </table>
        <table class="fin-table">
          <tr>
            <td class="title" colspan="3">Advanced Indicators</td>
          </tr>
          <tr>
            <td class="name"><UTooltip mode="top" :text="TooltipTexts['total_return']"/> Total Return (IRR)</td>
            <td v-if="Account.Basis.isPremium" class="value" v-colorBy:perf="financeModel.dto?.performance.irr">{{ $format['%'](financeModel.dto?.performance.irr) }}</td>
            <td v-if="!Account.Basis.isPremium" class="hidden" rowspan="3"><UnlockAnalytics>{{ $isMobile.value ? 'Unlock' : 'Unlock Analytics' }}</UnlockAnalytics></td>
          </tr>
          <tr>
            <td class="name"><UTooltip mode="top" :text="TooltipTexts['operating_expense_ratio']"/> Operating Expense Ratio (Year 1)</td>
            <td v-if="Account.Basis.isPremium" class="value">{{ $format['%'](financeModel.dto?.performance.operating_expense_ratio_year1) }}</td>
          </tr>
          <tr>
            <td class="name"><UTooltip mode="top" :text="TooltipTexts['debt_service_coverage']"/> Debt Service Coverage (Year 1)</td>
            <td v-if="Account.Basis.isPremium" class="value">{{ $format['number2Digits'](financeModel.dto?.performance.debt_service_coverage_year1) }}</td>
          </tr>
        </table>
      </div>
    </div>
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
.perfomance-dashboard {
  background: #f9f9f9;
  width: 100%;
  margin-top: 40px;

  .fin-table { 
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

  @media @mobile { margin-top: @mm; }
  > .flex {
    justify-content: space-between;
    align-content: stretch;
    align-items: stretch;

    @media @mobile { display: block; }
    > .side {
      padding: 0;
      width: calc(50% - 20px);

      @media @mobile { width: 100%; margin: 10px 0; }
    }
  }

}
</style>
