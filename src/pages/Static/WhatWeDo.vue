<template>
  <div class="static-page-header">
    <div class="wrapper">
      <h1 class="title">What we do</h1>
      <span class="text hide-mobile">Use real estate data and analysis to find lucrative traditional and Airbnb properties in a matter of minutes</span>
    </div>
  </div>
  <div class="services-block wrapper">
    <div class="title-block">
      <span class="title">Our Services</span>
      <span class="text">We serve clients around the world, helping them earn more and stay ahead in today’s highly competitive vacation rental market.</span>
    </div>
    <div class="services">
      <div class="flex">
        <div class="content">
          <span class="title">Distribution and Marketing</span>
          <span class="text">We take professional photos of your property and write search engine optimized content to create eye-catching listing and we promote it on the most viewed vacation rental websites in the world.</span>
          <UButton class="ui-btn-text">Get started</UButton>
        </div>
        <div class="image-block">
          <img src="@/assets/images/static/what-we-do/people-holding-magnifying-glass.svg" alt="people-holding-magnifying-glass" class="questions-image">
        </div>
      </div>
      <div class="flex">
        <div class="image-block">
          <img src="@/assets/images/static/what-we-do/woman-near-calendar.svg" alt="woman-near-calendar" class="questions-image">
        </div>
        <div class="content">
          <span class="title">Reservation Management</span>
          <span class="text">At VRRM we take care of the booking procedure from start to finish. We handle check in and check out, answer inquiries, manage deposits and payments, provide 24/7 customer support.</span>
          <UButton class="ui-btn-text">Get started</UButton>
        </div>
      </div>
      <div class="flex">
        <div class="content">
          <span class="title">Cleaning and Maintenance</span>
          <span class="text">We take professional photos of your property and write search engine optimized content to create eye-catching listing and we promote it on the most viewed vacation rental websites in the world.</span>
          <UButton class="ui-btn-text">Get started</UButton>
        </div>
        <div class="image-block">
          <img src="@/assets/images/static/what-we-do/people-washing-window.svg" alt="people-washing-window" class="questions-image">
        </div>
      </div>
      <div class="flex">
        <div class="image-block">
          <img src="@/assets/images/static/what-we-do/woman-watering-flower.svg" alt="woman-watering-flower" class="questions-image">
        </div>
        <div class="content">
          <span class="title">Revenue Management</span>
          <span class="text">At VRRM we take care of the booking procedure from start to finish. We handle check in and check out, answer inquiries, manage deposits and payments, provide 24/7 customer support.</span>
          <UButton class="ui-btn-text">Get started</UButton>
        </div>
      </div>
      <div class="flex">
        <div class="content">
          <span class="title">Accounting and Monthly Reports</span>
          <span class="text">We take professional photos of your property and write search engine optimized content to create eye-catching listing and we promote it on the most viewed vacation rental websites in the world.</span>
          <UButton class="ui-btn-text">Get started</UButton>
        </div>
        <div class="image-block">
          <img src="@/assets/images/static/what-we-do/woman-showing-stocks.svg" alt="woman-showing-stocks" class="questions-image">
        </div>
      </div>
    </div>
  </div>
  <UGetStarted />
  <UDivider />
  <OFRC_FAQ />
  <OFRC_FindInvestment wavePosition="top"/>
  <UFooter />
</template>
<style lang="less" scoped>
  span {
    display: block;
  }
  .static-page-header {
    background-image: url("../../assets/images/static/what-we-do/header-bg.png");
    background-position: center;
    -webkit-background-size: cover;
    -moz-background-size: cover;
    -o-background-size: cover;
    background-size: cover;
  }
  .title-block {
    text-align: center;
    width: 50%;
    margin: 0 auto;

    .title {
      font-size: 2.25rem;
      font-weight: 800;
    }
    .text {
      font-size: 1.125rem;
      font-weight: 600;
      line-height: 1.625rem;
      color: @col-text-gray-dark;
      margin-top: 24px;
    }
  }
  .services-block {
    margin-top: 60px;

    .content {
      width: 43%;
    }
    .services {
      @img-w: 28vw;
      > div {
        justify-content: space-between;
        align-items: center;
        margin-top: 80px;
      }
      .title {
        font-size: 1.875rem;
        font-weight: 800;
      }
      .text {
        font-size: 1.125rem;
        font-weight: 400;
        line-height: 1.75rem;
        color: @col-text-gray-dark;
        margin-top: 18px;
      }
      .ui-btn-text {
        text-transform: uppercase;
        font-weight: 800;
        margin-top: 22px;
      }
      img {
        width: @img-w;
        height: @img-w/1.5;
      }
    }
  }
</style>
<script lang="ts">
import {defineComponent} from 'vue';
import UButton from '@/components/ui/UButton.vue';
import UFooter from '@/components/static/footer.vue';
import OFRC_FindInvestment from '@/components/OFRC/FindInvestment.vue';
import UDivider from '@/components/ui/UDivider.vue';
import OFRC_FAQ from '@/components/OFRC/FAQ.vue';
import UGetStarted from '@/components/static/get-started.vue';

export default defineComponent({
  components:{
    UButton,
    UFooter,
    OFRC_FindInvestment,
    UDivider,
    OFRC_FAQ,
    UGetStarted
  },
  data() {
    return {
      radioModel1: undefined,
    }
  }
})
</script>