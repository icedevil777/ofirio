<template>
  <div class="popup-upgrade-content flex">
    <div class="start-free-trial-preview flex">
      <UIcon v-if="$isMobile.value" name="rocket" />
      <h1>{{ canUpgrade ? 'Upgrade Subscription' : 'Start 7 Day FREE Trial' }}</h1>
      <div class="plans">
        <URadio v-for="(p, i) of PriceModel" :key="p" v-model="paymentTypeIndex" name="payment-period-radio" :value="i" :class="{ 'selected': paymentTypeIndex == i }">
          <UIcon v-if="p.type == 'year'" name="crown" />
          <div class="plan flex">
            <span class="plan-name">{{ p.name }}</span>
            <div class="price-info">
              <span class="old-price">{{ $format['usd'](p.oldPrice) }}</span>
              <span class="price">{{ $format['usd'](p.priceMonthly) }}<span class="per-month">/mo</span></span>
            </div>
          </div>
        </URadio>
      </div>
      <UButton
        class="ui-btn ui-btn-green"
        :busy="upgradeBusy"
        @click="Account.Subscriptions.startSubscription(PriceModel[paymentTypeIndex].type)"
        v-if="!canUpgrade">
        Start FREE Trial
      </UButton>
      <span class="billed-info">Billed {{ PriceModel[paymentTypeIndex].name }} • Cancel Anytime</span>
      <div class="checklist" v-if="!$isMobile.value || !Account.Basis.isPremium">
        <div class="checklist-row flex">
          <UIcon name="checked-circle" />
          <span class="check-prop">Unlimited</span>
          <span class="check-name">Property Reports</span>
        </div>
        <div class="checklist-row flex">
          <UIcon name="checked-circle" />
          <span class="check-prop">Unlimited</span>
          <span class="check-name">Rent Analyzer Reports</span>
        </div>
        <div class="checklist-row flex">
          <UIcon name="checked-circle" />
          <span class="check-prop">Unlimited</span>
          <span class="check-name">Cap Rate Search</span>
        </div>
      </div>
      <UIcon class="ui-popup-default-close-icon" name="cross" @click="() => $root.$refs.popupUpgrade.close()" />
    </div>
    <div class="upgrade-preview" v-show="canUpgrade">
      <div class="check-preview">
        <h2>Order Review</h2>
        <table class="order-total">
          <tr>
            <td class="title">Current Plan ({{ currentPaymentPeriod.name }})</td>
            <td class="value">{{ $format['usd'](currentPaymentPeriod.priceMonthly * currentPaymentPeriod.monthCount)}}/{{ currentPaymentPeriod.nameShort }}</td>
          </tr>
          <tr>
            <td class="title">Upgrade Plan ({{ PriceModel[paymentTypeIndex].name }})</td>
            <td class="value">{{ $format['usd'](PriceModel[paymentTypeIndex].priceMonthly * PriceModel[paymentTypeIndex].monthCount) }}/{{ PriceModel[paymentTypeIndex].nameShort }}</td>
          </tr>
          <tr v-show="Account.Subscriptions.isPayable(PriceModel[paymentTypeIndex].type)">
            <td class="title">Remaining credit</td>
            <td class="value green">{{ $format['usd'](billPreview.total - PriceModel[paymentTypeIndex].priceMonthly * PriceModel[paymentTypeIndex].monthCount) }}</td>
          </tr>
          <tr class="divide">
            <td colspan="2"></td>
          </tr>
          <tr class="unavailiable" v-show="!Account.Subscriptions.isPayable(PriceModel[paymentTypeIndex].type)">
            <td class="title" colspan="2">Upgrade unavailiable</td>
          </tr>
          <tr class="total" v-show="Account.Subscriptions.isPayable(PriceModel[paymentTypeIndex].type)">
            <td class="title">Today's total</td>
            <td class="value">{{ $format['usd'](billPreview.total) }}</td>
          </tr>
        </table>
        <p class="description" v-show="Account.Subscriptions.isPayable(PriceModel[paymentTypeIndex].type)">Your remaining credit will be applied towards the upgrade.</p>
        <p class="description" v-show="Account.Subscriptions.isPayable(PriceModel[paymentTypeIndex].type)">Your subscription will renew on {{ $format['date'](billPreview.period_end) }} and you will be charged <span class="charge">{{ $format['usd'](PriceModel[paymentTypeIndex].priceMonthly * PriceModel[paymentTypeIndex].monthCount) }}</span> {{ PriceModel[paymentTypeIndex].name?.toLowerCase() }}</p>
      </div>
      <UButton
        class="ui-btn ui-btn-green"
        @click="Account.Restrictions.canUpgradeWith(PriceModel[paymentTypeIndex].type) && startUpgrade()"
        v-show="Account.Basis.isPremium"
        :class="{ disabled: !Account.Subscriptions.isPayable(PriceModel[paymentTypeIndex].type) || upgradeBusy }"
        :busy="upgradeBusy">
        Confirm
      </UButton>
      <p class="description ui-text-center" v-show="Account.Subscriptions.isPayable(PriceModel[paymentTypeIndex].type)">By clicking 'Confirm' you agree to be charged <span class="charge">{{ $format['usd'](billPreview.total) }}</span></p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

import UButton from '@/components/ui/UButton.vue';
import URadio from '@/components/ui/URadioInput.vue';
import UChipSelectGroup from '@/components/ui/UChipSelectGroup.vue';

import PriceModel from '@/models/Account/payments/paymentPrice';
import AccountStore from '@/models/Account';

export default defineComponent({
  components: {
    UButton,
    URadio,
    UChipSelectGroup
  },
  computed: {
    PriceModel() {
      return JSON.parse(JSON.stringify(PriceModel)).reverse();
    },
    Account() { return AccountStore; },
    currentPaymentPeriod() {
      if (!AccountStore.Basis.isPremium)
        return {};
      
      return PriceModel.find(pm => pm.type == AccountStore.Basis.dto?.subscription?.period);
    },
    canUpgrade() {
      return AccountStore.Basis.isPremium && !AccountStore.Basis.dto?.is_team && !AccountStore.Basis.dto?.subscription?.cancel_at_period_end;
    }
  },
  data() {
    return {
      paymentTypeIndex: 0,
      billPreview: {} as Record<string, string | number>,
      busyTime: Date.now(),
      upgradeBusy: false
    }
  },
  watch: {
    'paymentTypeIndex'(newVal) {
      this.updatePreview();
    }
  },
  methods: {
    startUpgrade() {
      const globMessages = (<any>this.$root).$refs.globMessages;

      //TODO: Confirm as a predefined type
      const selectedPaymentType = <any>(this.PriceModel[this.paymentTypeIndex].type);

      this.upgradeBusy = true;
      this.Account.Subscriptions.upgrade(selectedPaymentType)
      .then((result) => {
        if (result) {
          this.Account.Auth.loadAccountDTO();
          (<any>this.$root).$refs.popupUpgrade.close();
          return globMessages.push({ message: 'Success!', type: 'success' });
        }

        return globMessages.push({ message: 'Server error, please try again later', type: 'error' });
      })
      .catch((ex) => {
        return globMessages.push(ex);
      })
      .finally(() => {
        this.upgradeBusy = false;
      });
      
    },
    updatePreview() {
      const globMessages = (<any>this.$root).$refs.globMessages;

      //TODO: Confirm as a predefined type
      const selectedPaymentType = <any>(this.PriceModel[this.paymentTypeIndex].type);

      const ts = Date.now();
      this.busyTime = ts;
      this.billPreview = {};
      this.Account.Subscriptions.previewUpgrade(selectedPaymentType)
      .then((result) => {
        if (result != undefined && this.busyTime == ts)
          this.billPreview = result;
      })
      .catch((ex) => {
        return globMessages.push(ex);
      });
    }
  },
  mounted() {
    this.Account.Auth.initPromise.then(() => {
      
      if (!this.Account.Subscriptions.isPayable(<any>(this.PriceModel[this.paymentTypeIndex].type)))
        this.paymentTypeIndex++;

      if (this.canUpgrade && this.Account.Subscriptions.isPayable(<any>(this.PriceModel[this.paymentTypeIndex].type)))
        this.updatePreview();
      
    });
  }
  
})
</script>

<style lang="less" scoped>
.popup-upgrade-content {
  position: relative;
  justify-content: flex-start;
  align-content: flex-start;
  align-items: flex-start;
  width: auto;
  max-width: 1000px !important;
  padding: 40px 100px;
  background: linear-gradient(#fff 0%, #e1f9f2 100%) !important;

  @media @mobile {
    height: 100%;
    width: 100%;
    overflow-y: auto;
    padding: 50px 20px;
    display: block;
  }

  .start-free-trial-preview {
    flex-direction: column;
    align-content: center;
    align-items: center;

    > h1 {
      font-weight: 800;
      font-size: 1.875rem;
      margin-bottom: 30px;
    }
    > .svg-icon--rocket {
      @s: 50px;

      fill: @col-green;
      width: @s;
      min-width: @s;
      height: @s;
      min-height: @s;
      margin-bottom: 15px;
    }
    .plans {
      width: 400px;
      box-shadow: @shadow @col-shadow;
      border-radius: 10px;
      margin-bottom: 30px;
      position: relative;

      @media @mobile { width: 100%; }
      .plan {
        width: 100%;
        justify-content: space-between;
      }
      .svg-icon--crown {
        position: absolute;
        top: -4px;
        right: -4px;
        fill: #FFC700;
        background: @col-bg;
        border-radius: 50%;
        z-index: 1;
      }
      .plan-name {
        font-size: 1.125rem;
        font-weight: 800;

        @media @mobile { font-size: 1.25rem; }
      }
      .old-price {
        font-size: 0.875rem;
        font-weight: 800;
        color: @col-text-gray-darker;
        text-decoration: line-through;
        margin-right: 8px;

        @media @mobile { font-size: 1rem; }
      }
      .price {
        font-size: 1.125rem;
        font-weight: 800;

        .per-month {
          font-size: 0.875rem;
          font-weight: 500;
          color: @col-text-gray-darker;
        }
        @media @mobile {
          font-size: 1.25rem;

          .per-month { font-size: 1rem; }
        }
      }
    }
    .ui-radio {
      width: 100%;
      display: block;
      height: 60px;

      &:first-child { border-radius: 10px 10px 0 0; }
      &:last-child { border-radius: 0 0 10px 10px; }
      &.selected {
        background: #efeef9;

        .plan-name { color: @col-blue; }
      }
      &::v-deep > label {
        &.active { font-weight: 500; }
        > span {
          &::before { top: 17px; }
          &::after { top: 23px; }
        }
      }
    }
    .ui-btn {
      width: 100%;
      padding: 16px 0;
      margin-bottom: 20px;

      @media @mobile {
        font-size: 1.25rem;
        font-weight: 800;
      }
    }
    .billed-info {
      color: @col-text-gray-dark;
      @media @mobile { font-size: 1.15rem; }
    }
    .checklist {
      margin: 30px auto 0;

      .checklist-row {
        margin-bottom: 20px;
        justify-content: flex-start;
        align-items: center;
      }
      .svg-icon--checked-circle {
        @s: 1rem;

        width: @s;
        height: @s;
        margin-right: 5px;
        fill: @col-green; 
      }
      .check-prop {
        color: @col-green;
        font-weight: 700;
        margin-right: 10px;
      }
      .check-name {
        font-weight: 600;
      }
      @media @mobile { font-size: 1.15rem; }
    }
  }
  .upgrade-preview {
    @media @desktop { margin-left: 60px; }
    @media @mobile { margin-top: 20px; }

    .check-preview {
      border-radius: @border-radius;
      box-shadow: @col-shadow @shadow;
      padding: 20px 30px;
      margin-bottom: 20px;

      > h2 {
        font-weight: 800;
        font-size: 1.25rem;
        margin-bottom: 20px;
        display: block;
        text-align: center;
      }
      .order-total {
        width: 100%;

        tr td {
          padding: 10px 5px;
          white-space: nowrap;

          &:first-child { font-weight: 400; }
          &:last-child {
            padding-left: 20px;
            text-align: right;
            font-weight: 700;
          }
          &.green { color: @col-green; }
        }
        tr.divide td {
          border-top: 1px dashed @col-gray-light;
          padding: 10px 0 0;
        }
        tr.total td, tr.unavailiable { font-weight: 700; }
        tr.unavailiable td { text-align: center; }
      }
      > .description {
        padding: 0 5px;
      }
    }
    > .ui-btn {
      width: 100%;
      height: 56px;
    }
    .description {
      margin: 10px 0;
      font-weight: 400;
      font-size: .875rem;
      line-height: 1.25rem;
      color: @col-text-gray-dark;

      .charge { text-decoration: underline; }
    }
  }
}
</style>