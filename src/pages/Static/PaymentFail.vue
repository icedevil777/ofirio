<template>
  <div class="wrapper">
    <UIcon name="cross" />
    <span class="title">Payment Failed</span>
    <span class="text">We’re sorry your payment was declined. Please try again or provide an alternative payment method.</span>
    <span class="text">Please contact us if you have any questions</span>
    <router-link :to="{ name: 'account-subscriptions'}">
      <UButton class="ui-btn ui-btn-green">Try Again</UButton>
    </router-link>
  </div>
  <OFRC_FindInvestment wavePosition="top"/>
  <UFooter />
</template>
<style lang="less" scoped>
  span { display: block; }
  .wrapper {
    margin: 70px auto;
    text-align: center;

    .svg-icon {
      width: 60px;
      height: 60px;
      fill: @col-err;
    }
    .title {
      font-size: 2.625rem;
      font-weight: 800;
      margin: 30px 0 40px 0;
    }
    .text {
      color: @col-text-gray-dark;
      margin-top: 22px;
    }
    .ui-btn {
      display: inline-block;
      margin-top: 30px;
      padding: 12px 120px;
    }

    @media @mobile {
      margin: 50px auto;
      padding: 0 20px;

      .svg-icon {
        width: 50px;
        height: 50px;
      }
      .title { font-size: 1.85rem; }
      .text {
        font-size: 1.15rem;
        line-height: 1.6rem;
      }
      .ui-btn {
        padding: 12px 0;
        width: 100%;
      }
    }
  }
</style>
<script lang="ts">
import { defineComponent } from 'vue'
import UButton from '@/components/ui/UButton.vue';
import OFRC_FindInvestment from '@/components/OFRC/FindInvestment.vue';
import UFooter from '@/components/static/footer.vue'

export default defineComponent({
  components: {
    UButton,
    OFRC_FindInvestment,
    UFooter
  }
})
</script>