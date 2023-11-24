<template>

  <div class="account-internal-padding upgrades" v-if="!Account.Basis.isPremium">
    <h1 class="heading">Premium Subscription</h1>
    <div class="account-sub-block">
      <span class="sub-heading">Choose your plan</span>
      <div class="plan" v-for="p of PriceModel" :key="p">
        <div class="plan-info">
          <span class="plan-name">{{ p.name }}</span>
          <span class="billed-info">Billed {{ p.name }}</span>
        </div>
        <div class="discount" v-if="p.type == 'year'">
          <UIcon name="crown" />
          <span>save 75%</span>
        </div>
        <div class="price-info">
          <span class="old-price">{{ $format['usd'](p.oldPrice) }}</span>
          <span class="price">{{ $format['usd'](p.priceMonthly) }}<span class="per-month">/mo</span></span>
        </div>
        <div class="upgrade-btn">
          <UButton
            class="ui-btn"
            :class="{
              'ui-btn-green': p.type == 'year',
              'ui-btn-bordered-green': p.type != 'year'
            }"
            @click="Account.Subscriptions.startSubscription(p.type)">
            Upgrade
          </UButton>
        </div>
      </div>
    </div>
  </div>


  <div class="account-internal-padding subs" v-if="Account.Basis.isPremium && !Account.Basis?.dto?.subscription?.cancel_at_period_end">
    <h1 class="heading">My subscription</h1>
    <div class="account-sub-block">
      <span class="header">Current plan</span>
      <!-- <span class="plan-name">{{ Account.Basis?.dto?.subscription?.plan }}</span> -->
      <p class="text">Invest smarter, save time, and grow your wealth quickly</p>
      <UButton class="ui-btn ui-btn-bordered-green" @click="$root.$refs.popupUpgrade.open" v-if="Account.Subscriptions.isPayable('year')">Upgrade</UButton>
      <div class="payment-info flex">
        <div class="block">
          <span class="header">Payment Method</span>
          <UIcon name="info-circle" /> **** {{ Account.Subscriptions.dto?.card_last_4 }}
        </div>
        <div class="block" v-if="Account.Subscriptions.dto">
          <span class="header">Next payment</span>
          {{ $format['usd'](Account.Subscriptions.dto?.next_payment_amount) }} on {{ $format['dateTime'](Account.Subscriptions.dto?.current_period_end) }}
        </div>
      </div>
      <UButton class="ui-btn-text ui-href-underline change-payment-method" @click="Account.Subscriptions.changePaymentMethod()">Change Payment Method</UButton>
      <UButton class="ui-btn-text ui-btn-text-gray cancel-subs" @click="() => $router.push('/account/subscription-cancel')">Cancel Subscription</UButton>
    </div>
  </div>


  <div class="account-internal-padding subs" v-if="Account.Basis.isPremium && Account.Basis.dto?.subscription.cancel_at_period_end">
    <h1 class="heading">My subscription</h1>
    <div class="account-sub-block">
      <span class="header">Subscription canceled</span>
      <span class="plan-name">{{ Account.Basis?.dto?.subscription?.plan }}</span>
      <p class="text">Invest smarter, save time, and grow your wealth quickly</p>
      <div class="payment-info flex">
        <div class="block" v-if="Account.Subscriptions.dto">
          <span class="header">Access untill</span>
          {{ $format['dateTime'](Account.Subscriptions.dto?.current_period_end) }}
        </div>
      </div>
    </div>
  </div>


  <div class="account-internal-padding payment-history" v-if="Account.Subscriptions.dto?.invoices">
    <div class="account-sub-block">
      <span class="heading">Transactions</span>
      <table class="ui-table ui-table--stripped ui-table--mobile-transform">
        <tr>
          <th>Date</th>
          <th>Description</th>
          <th>Period</th>
          <th>#</th>
          <th>Total</th>
          <th></th>
        </tr>
        <tr v-for="row in Account.Subscriptions.dto.invoices" :key="row">
          <td data-desc="Date">{{ $format['dateTime'](row.created) }}</td>
          <td data-desc="Description">{{ row.plan_description }}</td>
          <td data-desc="Period">{{ $format['dateTime'](row.period_start) }} - {{ $format['dateTime'](row.period_end) }}</td>
          <td data-desc="#">{{ row.number }}</td>
          <td data-desc="Total">{{ $format['usd'](row.total) }}</td>
          <td style="align-self: end">
            <a :href="row.invoice_url" target="_blank" class="ui-href ui-href-default">Payment details</a>
          </td>
        </tr>
      </table>
    </div>
  </div>
  <Footer />
</template>

<style lang="less" scoped>
.account-internal-padding {
  &.upgrades .heading {
    @media @mobile { font-size: 2rem; }
  }
} 
.upgrades .account-sub-block {
  padding: 0;

  > .sub-heading { padding: 30px 30px 0; }
  .plan {
    display: grid; 
    grid-auto-columns: 1fr; 
    grid-template-columns: 1fr 1fr 1fr max-content; 
    grid-template-rows: 1fr; 
    gap: 0px 0px; 
    grid-template-areas: 
      "plan-info discount price-info upgrade-btn";
    align-content: center;
    align-items: center;

    .plan-info { grid-area: plan-info; }
    .discount { grid-area: discount; }
    .price-info { grid-area: price-info; }
    .upgrade-btn { grid-area: upgrade-btn; }

    padding: 30px;
    &:nth-child(odd) { background: #f9f9f9; }

    @media @mobile {
      grid-auto-columns: 1fr; 
      grid-template-columns: 1fr 1fr; 
      grid-template-rows: min-content min-content 1fr; 
      gap: 0px 0px; 
      grid-template-areas: 
        "discount discount"
        "plan-info price-info"
        "upgrade-btn upgrade-btn";
    
      border-top: 1px solid @col-gray-light;
      padding: 20px 20px 25px;

      &:nth-child(odd) { background: transparent; }
    }

  }
  .plan-info {
    .plan-name {
      font-weight: 700;
      margin-bottom: 5px;
    }
    .billed-info {
      font-size: 0.875rem;
      color: @col-text-gray-dark;
    }
  }
  .discount {
    .svg-icon {
      @s: 24px;
      width: @s;
      height: @s;
      fill: #FFC700;
      margin-right: 8px;
      vertical-align: middle;
    }
    span {
      font-weight: 800;
      color: @col-green;
      text-transform: uppercase;
      display: inline;
      vertical-align: middle;
    }
    @media @mobile { margin-bottom: 10px; }
  }
  .price-info {
    span { display: inline; }
    .old-price {
      font-size: 0.875rem;
      font-weight: 700;
      color: @col-text-gray-darker;
      text-decoration: line-through;
      margin: 0 15px 0 0;
    }
    .price {
      font-weight: 800;

      .per-month {
        font-size: 0.875rem;
        color: @col-text-gray-darker;
      }
    }
    @media @mobile {
      text-align: end;

      .old-price {
        display: block;
        margin: 0 0 5px 0;
      }
    }
  }
  .upgrade-btn {
    .ui-btn {
      width: 100%;
      padding: 12px 0;
      width: 280px;
    }
    @media @mobile {
      margin-top: 20px;

      .ui-btn { width: 100%; }
    }
  }
}
.subs .account-sub-block {
  @m: 15px;

  > span.header {
    text-transform: uppercase;
    color: #C8C8C8;
    margin-bottom: @m;
    font-weight: 800;
  }
  > span.plan-name {
    text-transform: uppercase;
    font-size: 2.25rem;
    color: @col-green;
    margin-bottom: @m;
    font-weight: 800;
  }
  > p.text {
    line-height: 1.8rem;
    max-width: 600px;
    margin-bottom: @m;
    color: @col-text-gray-dark;

    + .ui-btn {
      margin: @m/2 0 @m;
      width: 100%;
      max-width: 140px;
    }
  }
  .payment-info {
    margin-top: 2*@m;
    justify-content: flex-start;
    align-items: flex-start;

    > .block {
      margin-right: 40px;
      vertical-align: middle;
      font-weight: 700;
      color: @col-text-dark;

      .header {
        color: @col-text-gray-darker;
        margin-bottom: @m;
        font-size: .9rem;

        @media @mobile { margin-bottom: 10px; }
      }
      .svg-icon {
        @s: 16px;
        width: @s;
        min-width: @s;
        height: @s;
        min-height: @s;
        margin: 0 @m 0 0;
      }

      @media @mobile {
        margin-right: 0;
        margin-bottom: 20px;
      }
    }
    @media @mobile {
      display: block;
    }
  }
  > .cancel-subs {
    position: absolute;
    right: 40px;
    top: 30px;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.875rem;
    color: @col-text-gray-darker;

    @media @mobile { position: static; }
  }
  .change-payment-method {
    margin-top: 20px;

    @media @mobile { margin: 0 0 25px 0; }
  }
}
.payment-history {

  > .account-sub-block {
    padding: 0;

    > .heading {
      padding: 20px 30px 0;
      font-weight: 800;
      font-size: 1.5rem;

      @media @mobile { padding: 20px; }
    }

    @media @mobile { padding-bottom: 10px; }
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';
import Footer from '@/components/static/footer.vue';
import UButton from '@/components/ui/UButton.vue';

import AccountStore from '@/models/Account';
import PriceModel from '@/models/Account/payments/paymentPrice';

export default defineComponent({
  components: {
    Footer,
    UButton
  },
  computed: {
    Account: function () {
      return AccountStore;
    },
    PriceModel: function () {
      return JSON.parse(JSON.stringify(PriceModel)).reverse();
    }
  }
})
</script>