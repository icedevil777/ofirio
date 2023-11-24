<template>
  <OFRC_FindInvestment ref="firstBlock" />
  <div class="what-we-do-container flex wrapper">
    <div class="sub-block">
      <UIcon name="stocks-increase" />
      <span class="title">Data Driven</span>
      <span class="text">Hundreds of millions data points analyzed - making data your competitive advantage</span>
    </div>
    <div class="sub-block">
      <UIcon name="paid-search" />
      <span class="title">Result Focused</span>
      <span class="text">Access key metrics - Cap Rate, Cash on Cash, and IRR for smart investing</span>
    </div>
    <div class="sub-block">
      <UIcon name="brain" />
      <span class="title">AI-Powered</span>
      <span class="text">Discover your next deal with our state-of-the-art machine learning algorithms</span>
    </div>
  </div>
  <UDivider class="hide-desktop"/>
  <div class="top-locations-container flex wrapper">
    <div class="title-block">
      <span class="title">Top Investment Properties</span>
      <span class="text">Spend less time searching and more time investing - quickly filter millions of properties to find the best deal</span>
      <router-link
        :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }"
        v-if="!$isMobile.value"
      >
        <UButton class="ui-btn-text">Search all properties<UIcon name="smooth-arrow" /></UButton>
      </router-link>
    </div>
    <div class="locations-block flex">
      <div class="property-item">
        <img class="property-image" src="../../assets/images/static/home/top-rental-property-1.png" alt="top-rental-property-1">
        <div class="property-content padded">
          <span class="property-address">1988 Sagebrush Cir</span>
          <span class="property-parameters">2 beds · 2 baths · 842 sq.ft</span>
          <span class="property-price">$164,400</span>
          <StatusLabel label="sold" />
          <div class="property-rate flex">
            <USmallProp value="13.80" label="Cash on Cash" postfix="%" colorScheme="green" />
            <USmallProp value="12.50" label="Cap rate" postfix="%" colorScheme="green"/>
            <USmallProp value="2,900" label="EST. rent" prefix="$" />
          </div>
        </div>
      </div>
      <div class="property-item">
        <img class="property-image" src="../../assets/images/static/home/top-rental-property-2.png" alt="top-rental-property-2">
        <div class="label-block flex">
          <StatusLabel label="new" />
          <StatusLabel label="good_deal" />
        </div>
        <div class="property-content padded">
          <span class="property-address">108 Forest Lakes Dr</span>
          <span class="property-parameters">2 beds · 2 baths · 1110 sq.ft</span>
          <span class="property-price">$164,500</span>
          <StatusLabel label="sold" />
          <div class="property-rate flex">
            <USmallProp value="17.50" label="Cash on Cash" postfix="%" colorScheme="green" />
            <USmallProp value="11.30" label="Cap rate" postfix="%" colorScheme="green" />
            <USmallProp value="2,300" label="EST. rent" prefix="$" />
          </div>
        </div>
      </div>
      <div class="property-item">
        <img class="property-image" src="../../assets/images/static/home/top-rental-property-3.png" alt="top-rental-property-3">
        <div class="property-content padded">
          <span class="property-address">9066 Albion Ln N</span>
          <span class="property-parameters">3 beds · 2 baths · 2408 sq.ft</span>
          <span class="property-price">$369,500</span>
          <StatusLabel label="sold" />
          <div class="property-rate flex">
            <USmallProp value="12.70" label="Cash on Cash" postfix="%" colorScheme="green" />
            <USmallProp value="10.50" label="Cap rate" postfix="%" colorScheme="green" />
            <USmallProp value="4,200" label="EST. rent" prefix="$" />
          </div>
        </div>
      </div>
    </div>
    <router-link
      :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }"
      v-if="$isMobile.value"
    >
      <UButton class="ui-btn-text">Search all properties<UIcon name="smooth-arrow" /></UButton>
    </router-link>
  </div>
  <UDivider />
  <div class="what-ofirio-do-container flex wrapper">
    <div class="title-block">
      <span class="container-intro">Everything you need in one place</span>
      <span class="title">We Analyze Millions of Properties for You</span>
      <span class="text">Turn months of difficult research into a few easy seconds with our all-in-one solution</span>
      <div class="stats flex">
        <div class="item">
          <span class="value">$235B</span>
          <span class="name">Total Property Value</span>
        </div>
        <div class="item">
          <span class="value">7M</span>
          <span class="name">Rentals</span>
        </div>
        <div class="item">
          <span class="value">20 Years</span>
          <span class="name">Property History</span>
        </div>
      </div>
      <UButton class="ui-btn ui-btn-green hide-mobile" @click="Account.Restrictions.canStartFreeTrial() && $root.$refs.popupUpgrade.open()">Start 7-Days FREE Trial</UButton>
    </div>
    <div class="sub-block">
      <div class="item">
        <UIcon name="search-property" />
        <div class="content">
          <span class="title">Investment Finder</span>
          <span class="description">Filter by Cap Rate, Cash on Cash, Total Return and many other investment metrics to find the best deals</span>
        </div>
      </div>
      <div class="item">
        <UIcon name="graph" />
        <div class="content">
          <span class="title">Rent Analyzer</span>
          <span class="description">Estimate how much a property will rent for and how it compares to other properties in the area</span>
        </div>
      </div>
      <div class="item">
        <UIcon name="estimate-calculator" />
        <div class="content">
          <span class="title">Investment Calculator</span>
          <span class="description">Tailor the expenses of a property to get the most accurate financial forecasts specifically for you</span>
        </div>
      </div>
      <div class="item">
        <UIcon name="order-history" />
        <div class="content">
          <span class="title">Investment Forecasts</span>
          <span class="description">See how the property will perform over time taking into account all expenses and revenues</span>
        </div>
      </div>
    </div>
    <UButton class="ui-btn ui-btn-green hide-desktop" @click="Account.Restrictions.canStartFreeTrial() && $root.$refs.popupUpgrade.open()">Start Your FREE Trial</UButton>
  </div>
  <UDivider />
  <div class="video-container flex wrapper">
    <div class="title-block">
      <span class="title">See How Ofirio Works</span>
      <span class="text">Learn how you can turn months of difficult research into just a few easy seconds with Ofirio</span>
    </div>
    <!-- <div class="video-block">
      <iframe src="https://player.vimeo.com/video/567390590?title=0&byline=0&portrait=0" width="672" height="378" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>
    </div> -->
  </div>
  <div class="how-ofirio-works-wrapper">
    <UStaticSidedBlock titleSide="left">
      <template v-slot:side>
        <span class="title">Investment Finder</span>
        <span class="text">Find the best deals on the market based on your investment preferences</span>
        <div class="points">
          <div class="points-item">
            <UIcon name="checkmark" />
            <span class="text">Use advanced investment metrics like Cap rate, Cash on Cash, IRR and much more</span>
          </div>
          <div class="points-item">
            <UIcon name="checkmark" />
            <span class="text">Search by city, state, zip code, or address</span>
          </div>
          <div class="points-item">
            <UIcon name="checkmark" />
            <span class="text">Save your custom search and get new listing notifications</span>
          </div>
        </div>
        <router-link :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }">
          <UButton :class="{'ui-btn ui-btn-green': !$isMobile.value, 'ui-btn-text': $isMobile.value}">Get Started</UButton>
        </router-link>
      </template>
      <template v-slot:image>
        <img v-if="$isMobile.value" src="@/assets/images/static/home/advanced-property-finder-mobile.png">
        <img v-else src="@/assets/images/static/home/advanced-property-finder-desktop.png">
      </template>
    </UStaticSidedBlock>
  </div>
  <div class="how-ofirio-works-wrapper">
    <UStaticSidedBlock titleSide="right">
      <template v-slot:side>
        <span class="title">Rent Analyzer</span>
        <span class="text">Find out how much a property will rent for and how it compares to similar properties</span>
        <div class="points">
          <div class="points-item">
            <UIcon name="checkmark" />
            <span class="text">Understand the property rent range</span>
          </div>
          <div class="points-item">
            <UIcon name="checkmark" />
            <span class="text">Compare rent by property and building type</span>
          </div>
          <div class="points-item">
            <UIcon name="checkmark" />
            <span class="text">Download and save detailed rent analysis reports</span>
          </div>
        </div>
        <router-link :to="{ name: 'rent-estimator' }">
          <UButton :class="{'ui-btn ui-btn-green': !$isMobile.value, 'ui-btn-text': $isMobile.value}">Get Started</UButton>
        </router-link>
      </template>
      <template v-slot:image>
        <img v-if="$isMobile.value" src="@/assets/images/static/home/advanced-rent-estimator-mobile.png">
        <img v-else src="@/assets/images/static/home/advanced-rent-estimator-desktop.png">
      </template>
    </UStaticSidedBlock>
  </div>
  <div class="how-ofirio-works-wrapper">
    <UStaticSidedBlock titleSide="left">
      <template v-slot:side>
        <span class="title">Expenses Calculator</span>
        <span class="text">Tailor the expenses of a property to get the most accurate financial forecasts specifically for you</span>
        <div class="points">
          <div class="points-item">
            <UIcon name="checkmark" />
            <span class="text">Complete breakdown of property expenses like vacancy, taxes, HOA fees, and more</span>
          </div>
          <div class="points-item">
            <UIcon name="checkmark" />
            <span class="text">Understand expected monthly cash flow and other important financials</span>
          </div>
          <div class="points-item">
            <UIcon name="checkmark" />
            <span class="text">Fully customizable reports</span>
          </div>
        </div>
        <router-link :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }">
          <UButton :class="{'ui-btn ui-btn-green': !$isMobile.value, 'ui-btn-text': $isMobile.value}">Get Started</UButton>
        </router-link>
      </template>
      <template v-slot:image>
        <img v-if="$isMobile.value" src="@/assets/images/static/home/tailored-expanse-calculator-mobile.png">
        <img v-else src="@/assets/images/static/home/tailored-expanse-calculator-desktop.png">
      </template>
    </UStaticSidedBlock>
  </div>
  <div class="how-ofirio-works-wrapper">
    <UStaticSidedBlock titleSide="right">
      <template v-slot:side>
        <span class="title">Investment Forecasts</span>
        <span class="text">See how the property will perform over time taking into account all expenses and revenues</span>
        <div class="points">
          <div class="points-item">
            <UIcon name="checkmark" />
            <span class="text">Understand performance factors like Cap Rate, IRR, cash flow, and much more</span>
          </div>
          <div class="points-item">
            <UIcon name="checkmark" />
            <span class="text">See how much wealth the property will generate over its lifetime</span>
          </div>
          <div class="points-item">
            <UIcon name="checkmark" />
            <span class="text">Ditch your outdated spreadsheets!</span>
          </div>
        </div>
        <router-link :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }">
          <UButton :class="{'ui-btn ui-btn-green': !$isMobile.value, 'ui-btn-text': $isMobile.value}">Get Started</UButton>
        </router-link>
      </template>
      <template v-slot:image>
        <img v-if="$isMobile.value" src="@/assets/images/static/home/advanced-financial-forecasts-mobile.png">
        <img v-else src="@/assets/images/static/home/advanced-financial-forecasts-desktop.png">
      </template>
    </UStaticSidedBlock>
  </div>
  <UDivider />
  <USuccessStories />
  <UGetStarted />
  <div class="our-blog-container wrapper">
    <div class="title-block">
      <span class="title">Read our Blog</span>
      <span class="text">Was founded with the purpose to maximize your return on investment.</span>
    </div>
    <div class="blog-block flex">
      <div class="blog-item">
        <img class="blog-image" src="https://via.placeholder.com/100">
        <span class="date">February 21, 2020</span>
        <span class="title">The Most Important Indicator for Short-term Rental Property Managers</span>
        <UButton class="ui-btn-text">Read more</UButton>
      </div>
      <div class="blog-item">
        <img class="blog-image" src="https://via.placeholder.com/100">
        <span class="date">February 21, 2020</span>
        <span class="title">How to safely deal with the crisis? Deep cleaning is a great start</span>
        <UButton class="ui-btn-text">Read more</UButton>
      </div>
      <div class="blog-item">
        <img class="blog-image" src="https://via.placeholder.com/100">
        <span class="date">February 21, 2020</span>
        <span class="title">The Real Cost of Delivering First Class Results</span>
        <UButton class="ui-btn-text">Read more</UButton>
      </div>
    </div>
  </div>
  <UDivider />
  <OFRC_FAQ />
  <OFRC_FindInvestment wavePosition="top"/>
  <UFooter />
</template>
<style lang="less" scoped>
  span { display: block; }
  .ui-divider { 
    margin: 90px 0;
    @media @mobile { margin: 50px 0; }
  }
  .title-block {
    width: 30%;

    .container-intro {
      font-weight: 800;
      color: @col-text-gray-light;
      text-transform: uppercase;
      margin-bottom: 20px;
    }
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
      margin-top: 26px;
    }
    @media @mobile {
      width: 100%;
      text-align: center;

      .container-intro {
        font-size: 1.15rem;
      }
      .title {
        font-size: 1.85rem;
        line-height: 2.15rem;
      }
      .text {
        margin-top: 16px;
        font-size: 1.15rem;
        line-height: 1.5rem;
      }
    }
  }
  .what-we-do-container {
    margin: 50px auto 90px auto;
    justify-content: space-between;

    .sub-block {
      width: 30%;
      text-align: center;

      .title {
        font-size: 1.5rem;
        font-weight: 800;
        margin-top: 20px;
      }
      .text {
        font-weight: 400;
        line-height: 1.5rem;
        color: @col-text-gray-darker;
        margin-top: 18px;
      }
      &::v-deep .svg-icon {
        width: 50px;
        height: 50px;
        fill: @col-green;
      }
    }
    @media @mobile {
      display: block;
      padding: 0 20px;
      margin: 50px auto;

      .sub-block {
        width: 100%;
        margin-top: 30px;

        .title {
          font-size: 1.5rem;
        }
        .text {
          font-size: 1.15rem;
          line-height: 1.7rem;
        }
      }
    }
  }
  .top-locations-container {
    margin: 90px auto;
    justify-content: space-between;

    .ui-btn-text {
      margin-top: 26px;
      @arrow-s: 10px;
      display: inline-block;

      .svg-icon {
        width: @arrow-s;
        height: @arrow-s;
        margin-left: 10px;
        transform: rotate(90deg);
      }
    }
    .locations-block {
      .property-item {
        max-width: 236px;
        min-width: 236px;
        margin-right: 30px;
        border-radius: @border-radius;
        box-shadow: @shadow @col-shadow;
        position: relative;

        .property-image {
          border-radius: @border-radius @border-radius 0 0;
          width: 100%;
          height: 170px;
          padding: 0;
        }
        .property-content {
          &.padded { padding: 16px 20px; }

          .property-address {
            font-weight: 600;
            line-height: 1.1rem;
          }
          .property-parameters {
            margin-top: 4px;
            font-size: 0.875rem;
            font-weight: 500;
            line-height: 1.375rem;
            color: @col-text-gray-darker;
          }
          .property-price {
            margin-top: 10px;
            font-weight: 700;
            line-height: 1.2rem;
            display: inline-block;
            vertical-align: middle;
          }
          .property-rate {
            margin-top: 10px;
            justify-content: space-between;

            &::v-deep .ui-small-prop {
              .value { font-size: 1rem; }
              .label { font-size: 0.625rem; }
            }
          }
          .label {
            display: inline-block;
            margin: 10px 0 0 10px;
            vertical-align: middle;
          }
        }
        .label-block {
          position: absolute;
          top: 10px;
          left: 10px;

          .label { margin: 0 6px 0 0; }
        }
      }
    }
    @media @mobile {
      display: block;
      margin: 50px auto;

      &.wrapper { max-width: none; }
      .title-block { padding: 0 20px; }
      .ui-btn-text {
        padding: 0 20px;
        margin: 0 auto;
        display: block;
        text-align: center;
      }
      .locations-block {
        margin-top: 38px;
        overflow-x: auto;
        
        .property-item { margin: 20px 0 30px 20px; }
      }
    }
  }
  .what-ofirio-do-container {
    margin: 90px auto 120px auto;
    justify-content: space-between;

    .title-block {
      .stats {
        margin-top: 30px;
        justify-content: space-between;

        .item {
          .value {
            font-size: 1.875rem;
            font-weight: 700;
            color: @col-green;
            line-height: 2.2rem;
          }
          .name {
            font-size: 0.875rem;
            font-weight: 400;
            line-height: 1.5rem;
            color: @col-text-gray;
          }
        }
      }
    }
    .ui-btn {
      padding: 16px 60px;
      margin-top: 30px;
    }
    .sub-block {
      width: 50%;

      .item {
        position: relative;
        margin: 0 0 50px 80px;

        .svg-icon {
          position: absolute;
          width: 50px;
          height: 50px;
          left: -80px;
          fill: @col-green;
        }
        .title {
          font-size: 1.5rem;
          font-weight: 800;
        }
        .description {
          margin-top: 20px;
          font-weight: 400;
          color: @col-text-gray-darker;
          line-height: 1.5rem;
        }
      }
    }
    @media @mobile {
      display: block;
      padding: 0 20px;
      margin: 50px auto;

      .ui-btn {
        width: 100%;
        font-size: 1.3rem;
        padding: 16px 0;
      }
      .sub-block {
        width: 100%;
        margin-top: 48px;

        .item {
          margin: 0 0 38px 60px;

          .description { font-size: 1.15rem; }
          .svg-icon {
            left: -60px;
            top: -10px;
            width: 40px;
            height: 40px;
          }
        }
      }
    }
  }
  .video-container {
    margin: 90px auto;
    justify-content: space-between;
    align-items: center;

    iframe {
      border-radius: @border-radius;
    }
    @media @mobile {
      flex-direction: column;
      padding: 0 20px;
      margin: 50px auto;

      iframe {
        margin-top: 40px;
        width: 100%;
        height: 100%;
      }
    }

  }
  .how-ofirio-works-wrapper { overflow: hidden; }
  .our-blog-container {
    margin: 90px auto;
    text-align: center;
    // TODO: remove display none when blog will be ready
    display: none;

    .title-block {
      width: 100%;
    }
    .blog-block {
      margin-top: 50px;
      justify-content: space-around;

      .blog-item {
        max-width: 340px;
        min-width: 265px;
        text-align: initial;
        margin: 0 25px;

        .blog-image {
          width: 100%;
          height: 200px;
          border-radius: @border-radius;
        }
        .date {
          font-weight: 700;
          font-size: .875rem;
          color: @col-text-gray-darker;
          margin-top: 24px;
        }
        .title {
          font-weight: 800;
          font-size: 1.375rem;
          line-height: 1.6rem;
          margin-top: 16px;
        }
        .ui-btn-text {
          font-weight: 800;
          text-transform: uppercase;
          margin-top: 16px;
        }
      }

    }
    @media @mobile {
      padding: 0 20px;
      margin: 50px auto;

      .blog-block {
        overflow-x: auto;
        justify-content: flex-start;
        .blog-item {
          margin: 0 12px;
        }
      }
    }
  }
</style>
<script lang="ts">
import { defineComponent } from 'vue';
import UDivider from '@/components/ui/UDivider.vue';
import USmallProp from '@/components/ui/USmallProp.vue';
import UButton from '@/components/ui/UButton.vue';
import UFooter from '@/components/static/footer.vue';
import URadioChip from '@/components/ui/URadioChip.vue';
import UTextInput from '@/components/ui/UTextInput.vue';
import UShortInfo from '@/components/Property/sub/ShortInfo.vue';
import OFRC_FindInvestment from '@/components/OFRC/FindInvestment.vue';
import OFRC_FAQ from '@/components/OFRC/FAQ.vue';
import UGetStarted from '@/components/static/get-started.vue';
import USuccessStories from '@/components/static/success-stories.vue';
import StatusLabel from '@/components/Property/sub/StatusLabel.vue'
import UStaticSidedBlock from '@/components/ui/UStaticSidedBlock.vue'

import AccountStore from '@/models/Account';

export default defineComponent({
  components:{
    UDivider,
    USmallProp,
    UButton,
    UFooter,
    URadioChip,
    UTextInput,
    UShortInfo,
    OFRC_FindInvestment,
    OFRC_FAQ,
    UGetStarted,
    USuccessStories,
    StatusLabel,
    UStaticSidedBlock
  },
  computed: {
    Account() { return AccountStore; },
    appHeader(this:any) { return this.$root.$refs.header; }
  },
  methods: {
    onScroll() {
      const headerBr = this.appHeader.$el.getBoundingClientRect();
      const fbBr = (<any>this.$refs).firstBlock.$el.getBoundingClientRect();

      const isScrolled = fbBr.top + fbBr.height - headerBr.height < 0;
      this.appHeader.$el.classList.toggle('header-transparent', !isScrolled);
      this.appHeader.$el.classList.toggle('page-scrolled', isScrolled);
    }
  },
  mounted() {
    window.addEventListener('scroll', this.onScroll);
    this.appHeader.$el.classList.toggle('header-transparent', true);
    this.appHeader.$el.classList.toggle('page-scrolled', false);
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.onScroll);
    this.appHeader.$el.classList.toggle('header-transparent', false);
    this.appHeader.$el.classList.toggle('page-scrolled', false);
  }
})
</script>