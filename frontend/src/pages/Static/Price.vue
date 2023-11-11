<template>
  <div class="page-header">
    <h1 class="title">Upgrade to PREMIUM</h1>
    <h2 class="text">Save months of research and find the best deals in seconds</h2>
  </div>
  <div class="select-plan flex wrapper">
    <div v-for="p of PriceModel" :key="p" class="plan" :class="{ 'discounted-plan': p.type == 'year' }">
      <div class="discount" v-if="p.name == 'Annual'">
        <UIcon name="crown" />
        <span v-if="!$isMobile.value">Best discount - </span>
        <span class="value">save 75%</span>
      </div>
      <div class="plan-info">
        <span class="plan-name">{{ p.name }}</span>
      </div>
      <div class="price-info">
        <span class="old-price">{{ $format['usd'](p.oldPrice) }}</span>
        <span class="price">{{ $format['usd'](p.priceMonthly) }}<span class="per-month">/mo</span></span>
      </div>
      <div class="billed-info">
        <span class="billed-name">Billed {{ p.name }}</span>
      </div>
      <div class="select-btn">
        <UButton
          class="ui-btn ui-btn-green" 
          :class="{
            'ui-btn-transparant': p.name != 'Annual',
            'disabled': Account.Basis.isLoggedIn && !Account.Subscriptions.isPayable(p.type) 
          }" 
          @click="Account.Restrictions.canUpgradeWith(p.type) && Account.Subscriptions.startSubscription(p.type)">
          Select {{ $isMobile.value ? '' : p.name }}
        </UButton>
      </div>
      <div class="points" v-if="!$isMobile.value">
        <div class="point-item flex">
          <span class="value">Unlimited</span>
          <span class="text">Property Reports</span>
        </div>
        <div class="point-item flex">
          <span class="value">Unlimited</span>
          <span class="text">Rent Analyzer Reports</span>
        </div>
        <div class="point-item flex">
          <span class="value">Unlimited</span>
          <span class="text">Cap Rate Search</span>
        </div>
        <div class="point-item flex">
          <UIcon name="checkmark" />
          <span class="text">Nationwide Property Search</span>
        </div>
        <div class="point-item flex">
          <UIcon name="checkmark" />
          <span class="text">Advanced Filters</span>
        </div>
        <div class="point-item flex">
          <UIcon name="checkmark" />
          <span class="text">Custom Financial Forecasts</span>
        </div>
        <div class="point-item flex">
          <UIcon name="checkmark" />
          <span class="text">Property &amp; Tax History</span>
        </div>
        <div class="point-item flex">
          <UIcon name="checkmark" />
          <span class="text">AI-Powered Analytics</span>
        </div>
      </div>
    </div>
    <div class="points" v-if="$isMobile.value">
      <span class="title">Each plan includes:</span>
      <div class="point-item flex">
        <span class="value">Unlimited</span>
        <span class="text">Property Reports</span>
      </div>
      <div class="point-item flex">
        <span class="value">Unlimited</span>
        <span class="text">Rent Analyzer Reports</span>
      </div>
      <div class="point-item flex">
        <span class="value">Unlimited</span>
        <span class="text">Cap Rate Search</span>
      </div>
      <div class="point-item flex">
        <UIcon name="checkmark" />
        <span class="text">Nationwide Property Search</span>
      </div>
      <div class="point-item flex">
        <UIcon name="checkmark" />
        <span class="text">Advanced Filters</span>
      </div>
      <div class="point-item flex">
        <UIcon name="checkmark" />
        <span class="text">Custom Financial Forecasts</span>
      </div>
      <div class="point-item flex">
        <UIcon name="checkmark" />
        <span class="text">Property &amp; Tax History</span>
      </div>
      <div class="point-item flex">
        <UIcon name="checkmark" />
        <span class="text">AI-Powered Analytics</span>
      </div>
    </div>
  </div>
  <UDivider />
  <div class="ofirio-compare flex wrapper">
    <div class="title-block">
      <span class="title">Save BIG with Ofirio</span>
      <span class="text">Ofirio Replaces All Of Your Real Estate Tools</span>
      <UButton class="ui-btn ui-btn-green" v-if="!$isMobile.value" @click="Account.Restrictions.canUpgrade() && $root.$refs.popupUpgrade.open()">Upgrade to PREMIUM</UButton>
    </div>
    <div class="compare flex">
      <div class="ofirio-sub-block-compare">
        <div class="ofirio-sub-block">
          <div class="content padded">
            <img src="../../assets/icons/logo-full.svg" alt="logo-full">
            <div class="points">
              <div class="point-item">
                <UIcon name="checkmark" />
                <span class="text">AI-Powered Rent Analyzer</span>
              </div>
              <div class="point-item">
                <UIcon name="checkmark" />
                <span class="text">Rent Analyzer Reports</span>
              </div>
              <div class="point-item">
                <UIcon name="checkmark" />
                <span class="text">Nationwide Property Search</span>
              </div>
              <div class="point-item">
                <UIcon name="checkmark" />
                <span class="text">Advanced Filters</span>
              </div>
              <div class="point-item">
                <UIcon name="checkmark" />
                <span class="text">Custom Financial Forecasts</span>
              </div>
              <div class="point-item">
                <UIcon name="checkmark" />
                <span class="text">Property &amp; Tax History</span>
              </div>
              <div class="point-item">
                <UIcon name="checkmark" />
                <span class="text">Property Reports</span>
              </div>
            </div>
          </div>
        </div>
        <div class="compare-icon equal">
          <span>=</span>
        </div>
        <div class="compare-result">
          <span class="value">{{ $format['usd'](PriceModel[0].priceMonthly) }}</span>
          <span class="per-month">/mo.</span>
        </div>
      </div>
      <div class="vs-icon">VS</div>
      <span class="other-tools" v-if="$isMobile.value">Other tools</span>
      <div class="other-tools-sub-block-compare flex">
        <div class="content">
          <div class="tool-item padded">
            <span class="text">Rent Analyzer Tool (up to 10 reports)</span>
            <div class="price">
              <span class="value">$29.00</span>
              <span class="per-month">/mo.</span>
            </div>
            <span class="compare-icon plus">&plus;</span>
          </div>
          <div class="tool-item padded">
            <span class="text">Investment Finder Tool</span>
            <div class="price">
              <span class="value">$49.99</span>
              <span class="per-month">/mo.</span>
            </div>
            <span class="compare-icon plus">&plus;</span>
          </div>
          <div class="tool-item padded">
            <span class="text">Financial Analytics Tool</span>
            <div class="price">
              <span class="value">$29.99</span>
              <span class="per-month">/mo.</span>
            </div>
            <span class="compare-icon plus">&plus;</span>
          </div>
          <div class="tool-item padded">
            <span class="text">Property History Tool</span>
            <div class="price">
              <span class="value">$49.95</span>
              <span class="per-month">/mo.</span>
            </div>
          </div>
        </div>
        <div class="compare-icon equal">
          <span>=</span>
        </div>
        <div class="compare-result">
          <span class="value">$158.93</span>
          <span class="per-month">/mo.</span>
        </div>
      </div>
    </div>
    <UButton class="ui-btn ui-btn-green" v-if="$isMobile.value" @click="Account.Restrictions.canUpgrade() && $root.$refs.popupUpgrade.open()">Upgrade to PREMIUM</UButton>
  </div>
   <UDivider />
  <OFRC_FAQ />
  <UFooter />
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import UPageHeader from '@/components/ui/UPageHeader.vue'
import UDivider from '@/components/ui/UDivider.vue';
import UButton from '@/components/ui/UButton.vue';
import URadioChip from '@/components/ui/URadioChip.vue';
import UChipSelectGroup from '@/components/ui/UChipSelectGroup.vue';
import OFRC_FAQ from '@/components/OFRC/FAQ.vue';
import UFooter from '@/components/static/footer.vue';
import AccountStore from '@/models/Account';
import PriceModel from '@/models/Account/payments/paymentPrice';

export default defineComponent({
  components:{
    UPageHeader,
    UDivider,
    UButton,
    URadioChip,
    UChipSelectGroup,
    OFRC_FAQ,
    UFooter
  },
  computed: {
    Account() {
      return AccountStore;
    },
    PriceModel() {
      return JSON.parse(JSON.stringify(PriceModel)).reverse();
    }
  }
})
</script>

<style lang="less" scoped>
  span { display: block; }
  .page-header {
    text-align: center;
    padding: 50px 0 80px;

    .title {
      font-size: 2.625rem;
      font-weight: 800;
      margin-bottom: 15px;
    }
    .text {
      font-size: 1.25rem;
      font-weight: 600;
      color: @col-text-gray-dark;
    }

    @media @mobile {
      padding: 25px 20px;

      .title { font-size: 1.85rem; }
      .text {
        font-size: 1.15rem;
        line-height: 1.625rem;
      }
    }
  }
  .select-plan {
    justify-content: space-between;
    align-items: center;
    margin-bottom: 90px;

    .plan {
      display: grid;
      grid-template-rows: min-content min-content min-content min-content min-content;
      grid-auto-columns: 1fr;
      grid-auto-rows: 1fr;
      gap: 0px 0px;
      grid-auto-flow: row;
    }

    @media @mobile {
      display: block;

      &.wrapper {
        padding: 0 20px;
        max-width: none;
      }
      .plan {
        display: grid; 
        grid-template-columns: min-content min-content; 
        grid-template-rows: min-content min-content min-content; 
        gap: 0px 0px; 
        grid-template-areas: 
          "plan-info discount"
          "billed-info ."
          "price-info select-btn"; 
        justify-content: space-between; 
        align-items: end;

        border-radius: 10px;
        box-shadow: @shadow @col-shadow;
        padding: 25px 20px 20px;
        margin-bottom: 15px;

        &.discounted-plan {
          border: 2px solid @col-green;
          position: relative;
        }
      }
      .plan-info { grid-area: plan-info; }
      .billed-info { grid-area: billed-info; }
      .price-info { grid-area: price-info; }
      .discount { grid-area: discount; }
      .select-btn { grid-area: select-btn; }
    }

    .plan {
      border-radius: 20px;
      box-shadow: @shadow @col-shadow;
      text-align: center;
      padding: 30px 40px;

      &.discounted-plan {
        padding: 35px 40px 75px;
        border: 2px solid @col-green;
        position: relative;
      }

      @media @mobile {
        border-radius: 10px;
        box-shadow: @shadow @col-shadow;
        padding: 25px 20px 20px;
        margin-bottom: 15px;
        text-align: left;

        &.discounted-plan {
          padding: 25px 20px 20px;
          border: 2px solid @col-green;
        }
      }
    }
    .discount {
      font-weight: 800;
      color: @col-green;
      margin-bottom: 25px;
      text-transform: uppercase;
      align-self: start;

      .svg-icon {
        @s: 48px;
        position: absolute;
        top: 0 - @s/2;
        left: calc(50% - @s/2);
        width: @s;
        height: @s;
        fill: #FFC700;
        background: @col-bg;
      }
      span { display: inline; }
      .value { color: #007e59; }

      @media @mobile {
        margin-bottom: 0;
        .svg-icon {
          @s: 24px;
          
          vertical-align: middle;
          position: static;
          display: inline;
          width: @s;
          height: @s;
          fill: #FFC700;
          margin-right: 8px;
        }
        .value {
          font-weight: 800;
          vertical-align: middle;
          color: @col-green;
          text-transform: uppercase;
        }
      }
    }
    .plan-info {
      margin-bottom: 25px;

      .plan-name {
        font-size: 1.625rem;
        font-weight: 800;
      }
      @media @mobile { margin-bottom: 10px; }
    }
    .price-info {
      .old-price {
        font-size: 1.75rem;
        font-weight: 800;
        color: @col-text-gray-darker;
        text-decoration: line-through;
        margin-bottom: 5px;
      }
      .price {
        font-size: 2.625rem;
        font-weight: 800;
        margin-bottom: 10px;
  
        .per-month {
          font-size: 1.375rem;
          display: inline;
          color: @col-text-gray-darker;
        }
      }
      @media @mobile {
        .old-price {
          font-size: 1.15rem;
          font-weight: 700;
          display: inline;
          margin-right: 10px;
        }
        .price {
          font-size: 1.625rem;
          font-weight: 800;
          display: inline;

          .per-month {
            font-size: 1.15rem;
            display: inline;
          }
        }
      }
    }
    .billed-info {
      font-weight: 600;
      color: @col-text-gray-dark;
      margin-bottom: 30px;

      @media @mobile {
        margin-bottom: 0;
      }
    }
    .ui-btn {
      width: 100%;
      padding: 16px 0;

      &.ui-btn-transparant {
        background: none;
        color: @col-green;
        border: 2px solid @col-green;

        &.disabled {
          background: @col-disabled;
          color: @col-text-on-disabled;
          border: 2px solid @col-text-gray-darker;

          &:hover {
            background: @col-disabled;
            color: @col-text-on-disabled;

          }
        }
        &:hover {
          background: @col-green;
          color: @col-text-light;
        }
      }
      @media @mobile {
        font-size: 1.25rem;
        padding: 13px 20px;
      }
    }
    .points {
      margin-top: 30px;

      .point-item + .point-item { margin-top: 25px; }
      .point-item {
        font-weight: 600;

        .value, .svg-icon {
          color: @col-green;
          margin-right: 10px;
          font-weight: 700;
        }
        .svg-icon {
          width: 18px;
          height: 18px;
        }
      }
      @media @mobile {
        text-align: center;
        margin: 40px auto 0;
        max-width: 270px;

        .title {
          font-size: 1.625rem;
          font-weight: 800;
          margin-bottom: 25px;
        }
      }
    }
  }
  .ofirio-compare {
    margin-top: 90px;
    margin-bottom: 90px;
    justify-content: space-between;

    .title-block {
      width: 23%;

      .title {
        font-size: 2.25rem;
        font-weight: 800;
        line-height: 2.6rem;
      }
      .text {
        font-size: 1.125rem;
        font-weight: 600;
        line-height: 1.625rem;
        color: @col-text-gray-darker;
        margin-top: 25px;
      }
    }
    .ui-btn {
      width: 100%;
      padding: 16px 0;
      margin-top: 30px;
      font-weight: 800;
    }
    .compare {
      justify-content: center;
      position: relative;

      .compare-result {
        padding: 20px 0;
        width: 100%;
        border-radius: @border-radius;
        text-align: center;
  
        span {
          display: inline;
        }
        .value {
          font-size: 1.5rem;
          font-weight: 800;
        }
        .per-month {
          font-size: 1.125rem;
          color: @col-text-gray-dark;
        }
      }
      .compare-icon {
        @icon-s: 2rem;
        position: absolute;
        text-align: center;
        vertical-align: middle;
        font-size: @icon-s;
        line-height: @icon-s;        
        width: @icon-s;
        height: @icon-s;
        border-radius: 50%;
        background: @col-bg;
        box-shadow: @shadow @col-shadow;

        &.plus {
          z-index: 1;
          bottom: -20px;
          left: calc(50% - @icon-s/2);
        }
        &.equal {
          bottom: 54px;
          left: calc(50% - @icon-s/2);
        }
      }
      .vs-icon {
        @s: 4rem;
        z-index: 1;
        position: absolute;
        top: calc(50% - @s/2);
        left: calc(50% - @s/2);
        border-radius: 50%;
        font-size: @s/2.25;
        line-height: @s;
        font-weight: 800;
        background: @col-text-dark;
        color: @col-text-light;
        text-align: center;
        width: @s;
        height: @s;
        box-shadow: @shadow @col-shadow;
      }
      .other-tools {
        font-size: 1.625rem;
        font-weight: 800;
        margin: 20px 0;
        text-align: center;
      }
    }
    .ofirio-sub-block-compare {
      position: relative;
      margin-right: 50px;

      .content { margin-bottom: 10px; }
      .ofirio-sub-block {
        border-radius: @border-radius;
        background: @col-disabled;
  
        .padded {
          padding-top: 30px;
          padding-bottom: 30px;
        }
        img {
          height: 50px;
        }
        .points {
          span {
            display: inline;
            font-size: 1.125rem;
            font-weight: 800;
            margin-left: 12px;
          }
          .point-item {
            margin-top: 20px;
  
            .svg-icon {
              width: 16px;
              height: 14px;
              fill: @col-green;
            }
          }
        }
      }
      .compare-result {
        background: #E6FAF4;
        .value {
          color: @col-green;
        }
      }
    }
    .other-tools-sub-block-compare {
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      width: 360px;

      .tool-item {
        position: relative;
        background: @col-disabled;
        border-radius: @border-radius;
        margin-bottom: 10px;

        &.padded { padding: 20px 30px; }
        .text {
          font-size: 1.125rem;
          font-weight: 800;
        }
        .price {
          margin-top: 6px;

          span {
            display: inline;
          }
          .value {
            font-weight: 700;
            color: @col-err;
          }
          .per-month {
            color: @col-text-gray-dark;
          }
        }
      }
      .compare-result {
        background: #FEECEB;
        .value {
          color: @col-err;
        }
      }
    }
    @media @mobile {
      padding: 0 20px;
      display: block;

      .title-block {
        width: 100%;
        text-align: center;

        .title {
          font-size: 1.85rem;
          line-height: 2.15rem;
        }
        .text {
          font-size: 1.15rem;
          margin-top: 15px;
        }
      }
      .ui-btn {
        width: 83%;
        display: block;
        margin: 40px auto 0 auto;
      }
      .compare {
        display: block;
        width: 100%;
        margin-top: 40px;
        .ofirio-sub-block-compare {
          margin: 0;
          .padded { padding: 24px 20px 30px; }
          img {
            height: 34px;
            width: 96px;
          }
        }
        .vs-icon {
          @s: 3.5rem;
          z-index: 1;
          position: static;
          margin: 20px auto;
          font-size: @s/2.25;
          line-height: @s;
          width: @s;
          height: @s;
        }
        .other-tools-sub-block-compare {
          width: 100%;
        }
      }
    }
  }
</style>