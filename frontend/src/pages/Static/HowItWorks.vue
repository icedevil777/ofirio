<template>
  <UPageHeader>
    <h1 class="title">Investing Made Easy</h1>
    <p class="text hide-mobile">Find the best deals in seconds, maximize your return on investment, and grow your wealth quickly</p>
    <UButton class="ui-btn ui-btn-green" @click="() => $refs.videoPopup.open()">
        <UIcon name="play-circle" />
        <span>See How It Works</span>
    </UButton>
  </UPageHeader>
  <!-- <UPopup ref="videoPopup" @stateChange="(state) => reloadVideo(state)">
    <iframe ref="vimeoVideo" src="https://player.vimeo.com/video/567390590?title=0&byline=0&portrait=0" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>
  </UPopup> -->
  <div class="steps-block wrapper">
    <div class="title-block">
      <h1 class="title">How It Works</h1>
      <span class="text">Turn months of difficult research into a few easy seconds</span>
    </div>
    <div class="steps-icons flex">
      <div>
        <div>
          <UIcon name="search-property" />
        </div>
        <span>1. Investment Finder</span>
      </div>
      <div>
        <div>
          <UIcon name="graph" />
        </div>
        <span>2. Rent Analyzer</span>
      </div>
      <div>
        <div>
          <UIcon name="estimate-calculator" />
        </div>
        <span>3. Investment Calculator</span>
      </div>
      <div>
        <div>
          <UIcon name="order-history" />
        </div>
        <span>4. Investment Forecast</span>
      </div>
      <div>
        <div>
          <UIcon name="contact-us" />
        </div>
        <span>5. Close the Deal</span>
      </div>
    </div>
    <div class="steps-detailed">
      <ol>
        <li>
          <div class="flex">
            <div class="content">
              <span class="title">Investment Finder</span>
              <span class="text">
                Filter millions of properties in seconds. Search by advanced criteria such as Cash Flow, Cash on Cash Return, Capitalization Rate, Estimated Rent, and many other critical investment specifications.
              </span>
              <router-link
                :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }"
                v-if="!$isMobile.value"
              >
                <UButton class="ui-btn-text">Get Started</UButton>
              </router-link>
            </div>
            <div class="image-block">
              <img class="image-item" src="../../assets/images/static/how-it-works/investment-finder.svg" alt="investment finder">
            </div>
            <router-link
              :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }"
              v-if="$isMobile.value"
            >
              <UButton class="ui-btn-text">Get Started</UButton>
            </router-link>
          </div>
        </li>
        <li>
          <div class="flex title-rigth">
            <div class="content">
              <span class="title">Rent Analyzer</span>
              <span class="text">
                Get accurate and detailed rent estimates for any address, city, or zip code to understand how much rental income a property can generate and how it compares to other surrounding properties.
              </span>
              <router-link
                :to="{ name: 'rent-estimator' }"
                v-if="!$isMobile.value"
              >
                <UButton class="ui-btn-text">Get Started</UButton>
              </router-link>
            </div>
            <div class="image-block">
              <img class="image-item" src="../../assets/images/static/how-it-works/rent-analyzer.svg">
            </div>
            <router-link
              :to="{ name: 'rent-estimator' }"
              v-if="$isMobile.value"
            >
              <UButton class="ui-btn-text">Get Started</UButton>
            </router-link>
          </div>
        </li>
        <li>
          <div class="flex">
            <div class="content">
              <span class="title">Investment Calculator</span>
              <span class="text">
                Tailor any income or expense to understand how the investment will perform. Edit assumptions such as vacancy allowance, property appreciation rate, rental income appreciation, management fees, and many more.
              </span>
              <router-link
                :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }"
                v-if="!$isMobile.value"
              >
                <UButton class="ui-btn-text">Get Started</UButton>
              </router-link>
            </div>
            <div class="image-block">
              <img class="image-item" src="../../assets/images/static/how-it-works/investment-calculator.svg">
            </div>
            <router-link
              :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }"
              v-if="$isMobile.value"
            >
              <UButton class="ui-btn-text">Get Started</UButton>
            </router-link>
          </div>
        </li>
        <li>
          <div class="flex  title-rigth">
            <div class="content">
              <span class="title">Investment Forecast</span>
              <span class="text">
                Get a detailed financial report that includes the full projected performance of the property over its lifetime. See how much wealth the property will generate taking everything into account, including property appreciation, cash flow, mortgage paydown, and much more.
              </span>
              <router-link
                :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }"
                v-if="!$isMobile.value"
              >
                <UButton class="ui-btn-text">Get Started</UButton>
              </router-link>
            </div>
            <div class="image-block">
              <img class="image-item" src="../../assets/images/static/how-it-works/investment-forecast.svg">
            </div>
            <router-link
              :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }"
              v-if="$isMobile.value"
            >
              <UButton class="ui-btn-text">Get Started</UButton>
            </router-link>
          </div>
        </li>
        <li>
          <div class="flex">
            <div class="content">
              <span class="title">Close the Deal</span>
              <span class="text">
                Once you select a property, contact an agent for assistance with the transaction.
              </span>
              <router-link
                :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }"
                v-if="!$isMobile.value"
              >
                <UButton class="ui-btn-text">Get Started</UButton>
              </router-link>
            </div>
            <div class="image-block">
              <img class="image-item" src="../../assets/images/static/how-it-works/close-the-deal.svg">
            </div>
            <router-link
              :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }"
              v-if="$isMobile.value"
            >
              <UButton class="ui-btn-text">Get Started</UButton>
            </router-link>
          </div>
        </li>
      </ol>
    </div>
  </div>
  <div class="video-block">
    <div class="wrapper-wide">
      <span class="container-intro">WATCH Video</span>
      <span class="title">See How It Works</span>
      <UButton @click="() => $refs.videoPopup.open()">
        <UIcon name="play-circle" />
      </UButton>
    </div>
  </div>
  <USuccessStories />
  <OFRC_FindInvestment wavePosition="top"/>
  <UFooter />
</template>

<script lang="ts">
import {defineComponent} from 'vue';
import UPageHeader from '@/components/ui/UPageHeader.vue'
import UButton from '@/components/ui/UButton.vue';
import UPopup from '@/components/ui/UPopup.vue';
import UFooter from '@/components/static/footer.vue';
import OFRC_FindInvestment from '@/components/OFRC/FindInvestment.vue';
import USuccessStories from '@/components/static/success-stories.vue';
import AccountStore from '@/models/Account';

export default defineComponent({
  components:{
    UPageHeader,
    UButton,
    UPopup,
    UFooter,
    OFRC_FindInvestment,
    USuccessStories,
  },
  computed: {
    AccountStore() { return AccountStore; }
  },
  methods: {
    reloadVideo(state:boolean) {
      const iframe = <any>this.$refs.vimeoVideo;

      if (!state) {
        let iframeSrc = iframe.src;
        iframe.src = iframeSrc;
      }
    }
  }
})
</script>

<style lang="less" scoped>
  .static-page-header {
    background-image: url("../../assets/images/static/how-it-works/header-bg.png");

    .ui-btn {
      margin-top: 30px;
      padding: 8px 50px;

      span {
        display: inline;
        vertical-align: middle;
      }
      .svg-icon {
        width: 30px;
        vertical-align: middle;
        height: 30px;
        margin-right: 10px;
      }
    }
  }
  span { display: block; }
  iframe {
    width: 900px;
    height: 500px;

    @media @mobile { height: calc(100vw/1.8); }
  }
  .steps-block {
    margin-top: 60px;

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
    .steps-icons {
      @icon-w: 50px;
      @icon-h: 50px;
      justify-content: space-between;
      position: relative;
      margin-top: 60px;

      span {
        font-size: 1.25rem;
        font-weight: 800;
        margin-top: 28px;
        line-height: 1.5rem;
      }
      > div {
        z-index: 1;
        width: 16%;
        text-align: center;

        div {
          margin: 0 auto;
          width: fit-content;
          background: @col-bg;
          padding: 0 30px;
        }
      }
      .svg-icon {
        width: @icon-w;
        height: @icon-h;
        fill: @col-green;
      }
      &::after {
        content: "";
        position: absolute;
        width: 90%;
        top: 26px;
        left: 50%;
        transform: translate(-50%, -50%);
        border-top: 2px dashed @col-gray;
        z-index: 0;
      }
    }
    .steps-detailed {
      margin-top: 90px;
      @counter-font-s: 1.5rem;
      @counter-s: calc(2.5 * @counter-font-s);

      li {
        margin-top: 90px;
        counter-increment: count;
        position: relative;

        > div {
          justify-content: space-between;
          align-items: center;
        }
      }
      .title-rigth {
        .content { order: 1; }
      }
      .image-block {
        width: 40%;
        img { width: 100%; }
      }
      .content {
        width: 40%;

        &::before {
          content: counter(count);
          position: absolute;
          width: @counter-s;
          line-height: @counter-s;
          font-size: @counter-font-s;
          font-weight: 700;
          color: @col-green;
          border: 2px solid @col-green;
          border-radius: 50%;
          text-align: center;
          display: inline-block;
        }
        .title {
          font-size: 1.875rem;
          font-weight: 800;
          margin-top: calc(@counter-s + 20px);
        }
        .text {
          font-size: 1.125rem;
          font-weight: 400;
          line-height: 1.75rem;
          color: @col-text-gray-dark;
          margin-top: 18px;
        }
      }
      .ui-btn-text {
        text-transform: uppercase;
        font-weight: 800;
        margin-top: 22px;
      }
    }
    @media @mobile {
      padding: 0 25px;
      .title-block {
        width: 100%;
        .title {font-size: 1.85rem;}
        .text { font-size: 1.15rem; }
      }
      .steps-icons {
        display: block;
        margin: 40px auto 0 auto;
        width: fit-content;

        span {
          margin: 0 0 0 20px;
          display: inline;
          font-size: 1.3rem;
          text-align: left;
        }
        > div {
          display: flex;
          position: relative;
          width: 100%;
          align-items: center;
          margin-top: 30px;

          > div {
            margin: 0;
            padding: 10px 0;
          }
        }
        .svg-icon {
          width: 40px;
          height: 40px;
        }
        &::after {
          content: "";
          position: absolute;
          height: 90%;
          width: 0;
          top: 0;
          left: 18px;
          transform: none;
          border-left: 2px dashed @col-gray;
        }
      }
      .steps-detailed {
        margin-top: 60px;
        @counter-font-s: 1.5rem;
        @counter-s: calc(2.5 * @counter-font-s);

        li {
          margin-top: calc(@counter-s + 70px);
          text-align: center;

          > div { display: block; }
          .content {
            width: 100%;
            .title {
              margin-top: 0;
            }
            &::before {
              top: calc(-1*@counter-s - 20px);
              right: calc(50% - @counter-s/2);
            }
          }
          .image-block {
            margin-top: 25px;
            width: 100%;
            img { width: 100%; }
          }
          .ui-btn-text {
            font-size: 1.15rem;
            font-weight: 800;
            margin: 25px auto 0 auto;
          }
        }
      }
    }
  }
  .video-block {
    margin: 140px auto;

    > div {
      background: @col-disabled;
      border-radius: @border-radius;
      text-align: center;
      padding: 50px 0 80px 0;
      position: relative;
      @icon-s: 100px;

      .container-intro {
        font-weight: 800;
        text-transform: uppercase;
        color: @col-text-gray-light;
      }
      .title {
        font-size: 2.25rem;
        font-weight: 800;
        margin-top: 20px;
      }
      .ui-button {
        position: absolute;
        bottom: calc(-1 * @icon-s/2);
        left: calc(50% - @icon-s/2);
        padding: 0;
      }
      .svg-icon {
        width: @icon-s;
        height: @icon-s;
        fill: @col-green;
        background: @col-bg;
        border-radius: 50%;
      }
    }
    @media @mobile {
      @icon-s: 60px;
      margin: 50px 0 80px 0;

      > div {
        border-radius: 0;
        max-width: 100%;
        padding: 40px 0 56px 0;

        .container-intro { font-size: 1.15rem; }
        .title { font-size: 1.85rem; }
        .ui-button {
          bottom: calc(-1 * @icon-s/2);
          left: calc(50% - @icon-s/2);
        }
        .svg-icon {
          width: @icon-s;
          height: @icon-s;
        }
      }
    }
  }
</style>