<template>
  <Header ref="header" />

  <router-view/>

  <UPopup
    ref="popupLogin"
    class="popup-login"
    @stateChange="() => state == false && $refs.authComponent.reset(300)"
  >
    <div class="popup-login-content flex">
      <AccountAuth
        ref="authComponent"
        @login-success="$refs.popupLogin.close()"
      />
      <StaticProfileCons />
      <UIcon class="ui-popup-default-close-icon" name="cross" @click="() => $root['ev-popup-login-close']()" />
    </div>
  </UPopup>

  <UPopup
    ref="popupUpgrade"
    class="popup-upgrade"
    @stateChange="(state) => state && AccountStore.Auth.isLoggedIn ? triggerPopupEvent() : undefined"
  >
    <UpgradePopup />
  </UPopup>

  <UPopup
    ref="popupCallUs"
    class="popup-callus"
  >
    <CallUsPopup ref="popupCallUsBody"/>
  </UPopup>

  <UButton class="ui-btn ui-btn-iconic ui-btn-circle to-top-page" @click="scrollTop" v-show="showScrollTopButton"><UIcon name="bold-arrow"/></UButton>


  <div class="ofirio-global-messages">
    <UMessageList ref="globMessages"/>
  </div>

  <CookieContest />
</template>

<style lang="less">
  @import './components/ui/_ui.less';
  @import './components/ui/_common.less';
  @import './components/ui/_header.less';

  .popup-login-content {
    position: relative;
    flex-direction: row-reverse;
    overflow: hidden;

    @media @mobile {
      width: 100%;
      height: 100%;
      display: block;
      overflow-y: auto;
      border-radius: 0;
    }
  }
  .to-top-page {
    position: fixed;
    bottom: 100px;
    right: 25px;
    z-index: 2;

    &.ui-button.ui-btn-circle {
      &:focus, &:active { background: @col-bg; } 
      &:hover { .svg-icon { fill: @col-text-gray-darker; } }
      .svg-icon {
        fill: @col-text-dark;
        @s: 18px;
        width: @s;
        height: @s;
        transition: fill ease 0.2s;

        :hover { fill: @col-text-gray-darker; }

        @media @mobile { &:hover { fill: @col-text-dark; } }
      }

      @media @mobile { &:hover { background: @col-bg; } }
    }
    &.ui-btn { background: @col-bg; }
  }
  .ofirio-global-messages {
    @p: 30px;

    position: fixed;
    bottom: @p;
    max-width: calc(100% - 2*@p);
    left: 50%;
    transform: translateX(-50%);
    z-index: 100000;

    @media @mobile {
      max-width: 90vw;
      width: 100%;
    }
  }
</style>

<script lang="ts">

import { defineComponent, watch } from 'vue'

import UPopup from '@/components/ui/UPopup.vue';
import UButton from '@/components/ui/UButton.vue';
import UMessageList from '@/components/ui/UMessageList.vue';
import AccountAuth from '@/components/Account/auth.vue';
import Header from '@/components/OFRC/Header.vue';
import CookieContest from '@/components/OFRC/CookieContest.vue';
import StaticProfileCons from '@/components/static/profile-cons.vue';

import UpgradePopup from '@/components/OFRC/Popup-Upgrade.vue';
import CallUsPopup from '@/components/OFRC/Popup-Contact-Us.vue';

import AccountStore from '@/models/Account';

export default defineComponent({
  components: {
    UPopup,
    UButton,
    UMessageList,
    StaticProfileCons,
    AccountAuth,
    Header,
    CookieContest,
    UpgradePopup,
    CallUsPopup
  },
  watch: {
    '$route.path'() {
      if (AccountStore.Auth.isLoggedIn && AccountStore.Basis.dto) {
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({
          user_id: AccountStore.Basis.dto.pk
        });
      }
    }
  },
  data() {
    return {
      mobileMenuOpened: false,
      showScrollTopButton: false
    }
  },
  methods: {
    'ev-popup-login-open': function (state?: string) {
      (<any>this.$refs).header.toggleMobileMenu(false);
      (<any>this.$refs).popupLogin.open();
      if (state)
        (<any>this.$refs).authComponent.setState(state);
    },
    'ev-popup-login-close': function () {
      (<any>this.$refs).popupLogin.close();
    },
    scrollTop() {
      window.scrollTo({top: 0, behavior: 'smooth'});
    },
    showScrollButton() {
      const supportPageOffset = window.pageXOffset !== undefined;
      const isCSS1Compat = ((document.compatMode || '') === "CSS1Compat");
      const offset = supportPageOffset ? window.pageYOffset : isCSS1Compat ? document.documentElement.scrollTop : document.body.scrollTop;
      if (offset > window.innerHeight/2)
        this.showScrollTopButton = true;
      else
        this.showScrollTopButton = false;
    },
    triggerPopupEvent() {
      window._learnq = window._learnq || [];
      window._learnq.push(['track', 'opened pop-up', {
        'from_page': this.$route.path
      }]);
    }
  },
  computed: {
    AccountStore () {
      return AccountStore;
    }
  },
  mounted() {
    window.addEventListener('scroll', this.showScrollButton);
    AccountStore.Restrictions.register(this.$root);
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.showScrollButton);
  }
})
</script>