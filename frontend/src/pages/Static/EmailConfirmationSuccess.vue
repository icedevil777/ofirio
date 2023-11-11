<template>
  <div class="wrapper">
    <UIcon name="checkmark-in-circle" />
    <span class="title">Email Confirmation Successful</span>
    <span class="text">Your email has been successfully confirmed</span>
    <span class="text">Email us at <a href="mailto:info@ofirio.com" class="ui-href ui-href-underline">info@ofirio.com</a> with any questions, suggestions, or feedback.</span>
    <UButton class="ui-btn ui-btn-green" @click="continueOnSite">Continue</UButton>
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
      fill: @col-success;
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
      padding: 15px 120px;
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
import { defineComponent } from 'vue';

import AccountStore from '@/models/Account';
import UButton from '@/components/ui/UButton.vue';
import OFRC_FindInvestment from '@/components/OFRC/FindInvestment.vue';
import UFooter from '@/components/static/footer.vue'

const defferedActionName = 'ofirio-deffered-upgrade-action';


export default defineComponent({
  components: {
    UButton,
    OFRC_FindInvestment,
    UFooter
  },
  methods: {
    continueOnSite() {
      let goTo = { name: 'search', params: { typeOptions: 'state_id=FL' } };

      try {
        localStorage.setItem('ofirio-saved-after-login-active', 'true');
        const savedGoTo = <any>(JSON.parse(<string>localStorage.getItem('ofirio-saved-after-login-url')));
        if (savedGoTo && (savedGoTo.name != 'search' || Object.keys(savedGoTo?.params).length > 0))
          goTo = savedGoTo;

        const defferedVladFlowUpgradeFlow = localStorage.getItem(defferedActionName);
        if (defferedVladFlowUpgradeFlow == 'true')
          localStorage.setItem(defferedActionName, 'active');
      } catch (ex) {}

      this.$router.push(goTo);

      const defferedVladFlowUpgradeFlow = localStorage.getItem(defferedActionName);

      if (defferedVladFlowUpgradeFlow == 'active') {
        AccountStore.Auth.initPromise.then(() => {
          if (AccountStore.Auth.isLoggedIn && !AccountStore.Basis.isPremium && !AccountStore.Basis.dto?.is_team)
            (<any>this.$root).$refs.popupUpgrade.open();
        });
        try {
          localStorage.removeItem(defferedActionName)
        } catch (ex) {}
      }
    }
  },
  mounted() {
    AccountStore.Auth.initPromise.then(() => {
      if (AccountStore.Auth.inited && AccountStore.Auth.isLoggedIn) {
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({
          event: 'email_verified',
          user_id: AccountStore.Basis.dto?.pk
        });
      }
    });
  }
})
</script>