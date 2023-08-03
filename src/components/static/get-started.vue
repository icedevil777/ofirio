<template>
  <div class="get-started wrapper-wide">
    <div class="content">
      <span class="title">Get Started Now!</span>
      <span class="text">Invest smarter, save time, and grow your wealth quickly with a simple, powerful, low-cost, all-in-one solution that does the hard work for you</span>
    </div>
    <UButton class="ui-btn ui-btn-green" @click="Account.Restrictions.canStartFreeTrial() && $root.$refs.popupUpgrade.open()">Try it FREE</UButton>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import UButton from '@/components/ui/UButton.vue';
import AccountStore from '@/models/Account';

export default defineComponent({
  components: {
    UButton
  },
  computed: {
    Account() {
      return AccountStore; 
    }
  }
})
</script>

<style lang="less" scoped>
  .get-started {
    padding: 60px 0;
    background-color: @col-blue;
    border-radius: @border-radius;
    text-align: center;

    &.wrapper-wide { margin: 90px auto; }
    .content {
      width: 50%;
      margin: 0 auto;

      span { display: block; }

      .title {
        font-size: 2.25rem;
        font-weight: 800;
        color: @col-text-light;
      }
      .text {
        font-size: 1.125rem;
        font-weight: 600;
        line-height: 1.625rem;
        color: @col-gray-light;
        margin-top: 25px;
      }
    }
    .ui-btn {
      padding: 16px 100px;
      font-weight: 800;
      margin-top: 35px;
    }
    @media @mobile {
      padding: 50px 0;
      border-radius: 0;
      max-width: 100%;
      
      .content {
        width: 80%;

        .title { font-size: 1.85rem;}
        .text {
          font-size: 1.15rem;
          margin-top: 15px;
        }
      }
      .ui-btn { margin-top: 30px; }
    }
  }
</style>