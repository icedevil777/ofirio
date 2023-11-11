<template>
  <div class="wrapper">
    <span class="title">Complete Verification</span>
    <span class="text">Thanks for creating an account.</span>
    <span class="text">
      To verify your email and see all the data Ofirio has to offer please accept our <router-link :to="{ name: 'static-terms-and-conditions' }" class="ui-href ui-href-underline">Terms of Use</router-link>.
    </span>
    <UButton class="ui-btn ui-btn-green" :class="{ disabled: !canBeDone }" @click="accept">Accept</UButton>
  </div>
  <UFooter />
</template>

<style lang="less" scoped>
  span { display: block; }
  .wrapper {
    margin: 15vh auto 5vh;
    text-align: center;
    min-height: 50vh;

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

import AccountStore from '@/models/Account';

const defferedActionName = 'ofirio-deffered-upgrade-action';


export default defineComponent({
  components: {
    UButton,
    OFRC_FindInvestment,
    UFooter
  },
  computed: {
    canBeDone() {
      //@ts-ignore WTF VUE?! why busy is not defined on {} ?!
      return AccountStore.Auth.inited && AccountStore.Auth.isLoggedIn && !this.busy;
    }
  },
  data() {
    return {
      busy: false
    }
  },
  methods: {
    accept() {
      if (!this.canBeDone)
        return;

      this.busy = true;
      AccountStore.Profile.acceptTermsOfUse()
      .then((result) => {
        if (!result)
          return;


        let goTo = '/';
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
      })
      .catch((message) => {
        (<any>this.$root).$refs.globMessages.push(message)
      })
      .finally(() => {
        this.busy = false;
      });

    }
  }
})
</script>