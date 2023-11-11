<template>
  <footer class="footer">
    <div class="flex wrapper">
      <div class="block logo-block">
        <UIcon name="logo-full-fff"/>
      </div>
      <div class="block">
        <span class="header">About Us</span>
        <router-link :to="{ name: 'static-about-us'}" class="ui-href">About Us</router-link>
      </div>
      <div class="block">
        <span class="header">Learn</span>
        <router-link :to="{ name: 'static-how-it-works'}" class="ui-href">How it works</router-link>
      </div>
      <div class="block">
        <span class="header">Services</span>
        <router-link :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }" class="ui-href">Investment Finder</router-link>
        <router-link :to="{ name: 'rent-estimator'}" class="ui-href">Rent Analyzer</router-link>
      </div>
      <div class="block">
        <span class="header">Contact us</span>
        <router-link :to="{ name: 'static-contact-us'}" class="ui-href">Contact Us</router-link>
        <a href="tel:+18885505978" class="ui-href">+1 888-550-5978</a>
        <a href="mailto:help@ofirio.com" class="ui-href">help@ofirio.com</a>
      </div>
    </div>
    <div class="wrapper low-block">
      <span class="copyright">Updated {{ effectiveDate }}: By searching, you agree to the <router-link :to="{ name: 'static-terms-and-conditions'}" class="ui-href-underline ui-href-dark">Terms of Use</router-link> and <router-link :to="{ name: 'static-privacy-policy'}" class="ui-href-underline ui-href-dark">Privacy Policy</router-link>.</span>
      <span class="copyright">
        <UIcon name="fair-housing-act" />
        Ofirio LLC and its subsidiaries fully support the principles of the <a href="https://www.hud.gov/program_offices/fair_housing_equal_opp" class="ui-href-underline ui-href-dark">Fair Housing Act.</a>
      </span>
      <span class="copyright">If you are using a screen-reader or having trouble reading this website, please contact Ofirio Customer Support to seek accommodation at <a href="mailto:help@ofirio.com" class="ui-href-underline ui-href-dark">help@ofirio.com</a></span>
      <span class="copyright">Ofirio FL LLC is a licensed real estate brokerage in Florida #CQ1063299</span>
      <span class="copyright">The main Ofirio LLC office is located in Wilmington, Delaware.</span>
      <span class="copyright">&copy; 2021 All rights reserved.</span>
    </div>
  </footer>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import envModel from '@/models/env.model'

export default defineComponent({
  computed: {
    effectiveDate() {
      return envModel.VUE_APP_TERMS_UPDATE_DATE;
    }
  }
})
</script>


<style lang="less" scoped>
footer {
  @p: 40px 30px;

  background: @col-text-dark;
  color: @col-text-gray-light;
  padding: @p;
  font-size: 0.9rem;

  @media @mobile {
    padding: 30px 25px;
  }

  .wrapper {
    justify-content: space-between;
    align-content: flex-start;
    align-items: flex-start;

    .block {
      .svg-icon--logo-full-fff {
        // taken from svg
        width: 97px;
        min-width: 97px;
        height: 37px;
        min-height: 37px;
      }
      .ui-href, .header {
        display: block;
        margin-bottom: 20px;
      }
      .header {
        color: @col-text-light;
        font-weight: 700;
      }
    }

    @media @mobile {
      justify-content: center;
      align-content: flex-start;
      flex-wrap: wrap;

      .block {
        width: 50%;
        margin-top: 20px;

        &.logo-block {
          width: 100%;
          margin: 0;
        }
        .svg-icon--logo-full-fff {
          width: 83px;
          min-width: 83px;
          height: 30px;
          min-height: 30px;
        }
      }
    }
  }
  .low-block {
    text-align: center;
    font-weight: 400;
    margin-top: 30px;

    .svg-icon {
      vertical-align: middle;
      margin-right: 5px;
    }
    .copyright {
      display: block;
      margin-top: 15px;

      @media @mobile { line-height: 1.3rem; }
    }
  }
}
</style>