<template>
  <nav class="nav-header flex padded" :class="[ 'route-page-' + $route.name ]">

    <div class="flex logo-side">
      <router-link to="/" class="logo">
        <UIcon class="hide-mobile" name="logo-full" />
        <UIcon class="hide-desktop" name="logo-short" />
      </router-link>
      <div class="search-bar"><SearchComponent ref="headerSearch"/></div>
    </div>
    <UButton class="ui-btn-text-black goback" @click="$router.back()"><UIcon name="smooth-arrow" /> Back</UButton>
    <UIcon class="mobile-menu-toggle hide-desktop" name="menu" @click="() => toggleMobileMenu(true)" />
    <div class="mobile-menu-bg hide-desktop" v-bind:class="{ active: mobileMenuOpened }" @click="() => toggleMobileMenu(false)"></div>
    <div class="flex right-side" v-bind:class="{ opened: mobileMenuOpened }" ref="rightMenu">
      <div class="empty hide-desktop"></div>
      <router-link
        custom
        v-slot="{ href, navigate }"
        :to="{ name: 'rent-estimator'}"
      >
        <UButton class="ui-btn-text rent-anal btn-link" :href="href" @click.prevent="() => { navigate(); toggleMobileMenu(false) }">Rent Analyzer</UButton>
      </router-link>
      
      <UCollapsible class="learn-container learn-collapsible hide-desktop" label="Learn">
        <div class="learn-drop-container" @click="() => toggleMobileMenu(false)">
          <router-link :to="{ name: 'static-how-it-works'}">How it works</router-link>
          <router-link :to="{ name: 'static-about-us'}">About Us</router-link>
        </div>
      </UCollapsible>
      <UDrop class="learn-container learn-drop hide-mobile" label="Learn" ref="learnDropMenu">
        <template v-slot:content="{ props }">
          <div class="learn-drop-container" @click="() => { props.close(); toggleMobileMenu(false) }">
            <router-link :to="{ name: 'static-how-it-works'}">How it works</router-link>
            <router-link :to="{ name: 'static-about-us'}">About Us</router-link>
          </div>
        </template>
      </UDrop>
      <router-link
        custom
        v-slot="{ href, navigate }"
        :to="{ name: 'static-price'}"
      >
        <UButton class="ui-btn-text ui-btn-text-black btn-link" :href="href" @click.prevent="() => { navigate(); toggleMobileMenu(false) }">Pricing</UButton>
      </router-link>
      
      <router-link class="link-favorites hide-mobile" :to="{ name: 'account-favorites'}" v-if="Account.Basis.isLoggedIn" @click="toggleMobileMenu(false)"><UIcon name="heart" /><span class="ui-counter">{{ Account.Basis.dto.favorites_qty }}</span></router-link>
      <UDrop class="account-drop" v-if="Account.Basis.isLoggedIn" ref="accountDropMenu">
        <template v-slot:label><UIcon name="user-color"/> Hello, {{ Account.Basis.dto.first_name || 'Stranger' }}</template>
        <template v-slot:content="{ props }">
          <AccountInfo :afterNavigate="props.close" />
          <UDivider />
          <div class="link-section" @click="() => { props.close(); toggleMobileMenu(false) }">
            <router-link to="/account/favorites" class="flex favorites">Favorites <span class="ui-counter">{{ Account.Basis.dto.favorites_qty }}</span></router-link>
            <router-link to="/account/reports">Reports</router-link>
          </div>
          <UDivider />
          <div class="link-section" @click="() => { props.close(); toggleMobileMenu(false) }">
            <router-link to="/account/subscription">Subscription</router-link>
            <router-link to="/account/settings">Account settings</router-link>
            <router-link to="/account/email-settings">Email settings</router-link>
          </div>
          <UDivider />
          <div class="link-section" @click="() => { props.close(); toggleMobileMenu(false) }">
            <UButton
              @click="Account.Auth.logout()"
              class="ui-btn-text ui-btn-text-gray btn-logout"
            >Log out</UButton>
          </div>
        </template>
      </UDrop>
      <UButton class="ui-btn ui-btn-bordered btn-login" v-if="!Account.Basis.isLoggedIn" @click="() => $root['ev-popup-login-open']('login')">Login</UButton>
      <UButton class="ui-btn ui-btn-green btn-trial" v-if="!Account.Basis.isLoggedIn" @click="onRegisterClick()">7-Days FREE Trial</UButton>
      <div class="mobile-logo-row hide-desktop">
        <UIcon name="logo-full" />
        <UIcon class="mobile-menu-close" name="cross" @click="toggleMobileMenu(false)" />
      </div>
    </div>
  </nav>
</template>

<style lang="less" scoped>
nav.nav-header {
  position: fixed;
  width: 100%;
  height: @header-height;
  top: 0;
  left: 0;
  box-shadow: 0 1px 12px @col-shadow;
  justify-content: space-between;
  align-items: center;
  background: @col-bg;
  z-index: 1000;

  &.route-page-static-home {
    &.header-transparent .logo-side .search-bar {
      opacity: 0;
      visibility: hidden;
    }
  }
  @media @mobile {
    height: @header-height-mobile;

    &.route-page-property .logo-side { display: none; }
    &.route-page-property .goback { display: flex; }
  }
  @media @desktop {
    &.route-page-search { box-shadow: none; }
  }
  .logo-side {
    justify-content: flex-start;
    align-items: center;
    max-width: 50vw;
    flex: 1;

    @media @mobile {
      max-width: none;
      margin-right: 20px;
    }
    .logo {
      display: block;
      flex: 0 0 auto;
      margin-right: 30px;

      @media @mobile { margin-right: 20px; }
      .svg-icon--logo-full {
        // taken from svg
        width: 97px;
        height: 37px;
      }
      .svg-icon--logo-short {
        // taken from svg
        width: 21px;
        height: 25px;
      }
    }
    .search-bar {
      flex: 1 0 auto;
      max-width: 100%;
      transition: .3s ease opacity, .3s ease visibility;

      @media @mobile {
        &::v-deep .svg-icon--magnifier { display: none; }
      }
    }
  }

  .goback {
    display: none;
    white-space: nowrap;
    justify-content: flex-start;
    align-items: center;
    margin: 0;
    padding: 0;
    font-weight: 600;
    font-size: 1rem;

    .svg-icon {
      @s: 16px;

      width: @s;
      min-width: @s;
      height: @s;
      min-height: @s;
      transform: rotate(270deg);
      margin: 0 10px 0 0;
    }
  }

  .mobile-menu-toggle {
    @s: 18px;

    width: @s;
    min-width: @s;
    height: @s;
    min-height: @s;
  }

  .mobile-menu-bg {
    position: fixed;
    top: 0;
    right: 0;
    left: 0;
    bottom: 0;
    background: @col-popup-bg;
    transition: opacity .3s ease, visibility .3s ease;
    visibility: hidden;
    opacity: 0;
    z-index: 100;

    &.active {
      visibility: visible;
      opacity: 1;
    }
  }

  .right-side {
    align-items: center;
    justify-content: flex-end;
    flex-shrink: 0;

    .mobile-logo-row {
      position: relative;
    }
    .svg-icon--logo-full {
      width: calc(100% - 40px);
      height: 40px;
      min-height: 40px;
      order: 2;
      margin: 0 20px 20px;
      padding-top: 10px;
    }
    .mobile-menu-close {
      @s: 16px;

      position: absolute;
      top: 10px + 30px/2 - @s/2;
      right: 20px;
      width: @s;
      height: @s;
    }
    > .ui-button {
      margin-left: 20px;
      white-space: nowrap;
      height: 40px;

      &.btn-link { line-height: 40px; }
      @media @mobile {
        width: calc(100% - 40px);
        margin: 0 20px 15px;

        &.ui-btn { text-align: center; }
      }
    }
    .learn-container {
      margin: 0 0 0 20px;

      &::v-deep > .ui-drop-label {
        box-shadow: none;
        font-weight: bold;
        background: transparent;
        transition: color .3s ease;

        &:hover { color: @col-blue; }
      }
      &::v-deep .learn-drop-container {
        padding: 10px 0;
        background: @col-bg;
        border-radius: @border-radius;

        > a {
          display: block;
          padding: 10px 20px;
          white-space: nowrap;
          transition: background .1s ease;

          &:hover, &:focus {
            background: @col-disabled;
          }
        }
      }
    }
    .link-favorites {
      margin-left: 20px;

      .svg-icon {
        @s: 18px;
        width: @s;
        height: @s;
        vertical-align: middle;
        margin: 0;
        margin-right: 5px;
        fill: @col-text-dark;
        transition: fill .2s ease;
      }
      &:hover .svg-icon {
        fill: @col-blue;
      }
    }
    .account-drop {

      @media @desktop { margin-left: 20px; }
      &::v-deep .ui-drop-label {
        @h: 40px;

        box-shadow: 0px 1px 5px @col-shadow;
        font-weight: bold;
        background: transparent;
        font-size: 0.9rem;
        height: @h;
        line-height: @h;
        border-radius: @h/2;
        padding: 5px 10px 5px 5px;

        .svg-icon {
          @s: 30px;

          margin: 0 10px 0 0;
          width: @s;
          height: @s;
          vertical-align: middle;
        }

        @media @mobile { display: none; }
      }
      &.opened::v-deep {
        .ui-drop-label { background: @col-disabled; }
        .ui-drop-container { transform: translate(0, 0); }
      }
        
      &::v-deep .ui-drop-container {
        @p: 20px;

        left: auto;
        right: 0;
        transform: translate(0, -20px);
        min-width: 280px;

        .scroll-container {
          max-height: none;
          overflow: visible;
        }
        .svg-icon--cross-bolder { display: none; }
        .ui-divider { margin: 0; }
        .account-info {
          padding: @p;
          
          @media @mobile {
            padding-top: 0;
          }
        }
        .link-section {
          padding: @p/2 0;

          > a {
            @h: 40px;

            width: 100%;
            height: @h;
            line-height: @h;
            padding: 0 @p;
            
            &.flex {
              align-items: center;
              align-content: center;
              justify-content: space-between;
            }
            &:not(.flex) {
              display: block;
            }
            &.favorites .ui-counter { background: @col-green; }
          }
          .btn-logout {
            font-weight: inherit;
            padding: @p/2 @p;
            width: 100%;
          }
        }

        @media @mobile {
          display: block;
          visibility: visible;
          opacity: 1;
          transform: none;
          position: static;
          width: 100%;
          box-shadow: none;
        }
      }

      @media @mobile {
        width: 100%;
      }
    }
    > .empty { flex: 1; }
    .rent-anal { color: @col-green; }

    @media @mobile {
      position: fixed;
      right: 0;
      transform: translateX(110%);
      top: 0;
      bottom: 0;
      overflow-y: auto;
      background: @col-bg;
      visibility: hidden;
      z-index: 150;
      max-width: 80%;
      min-width: 300px;
      flex-direction: column-reverse;
      align-items: flex-start;
      justify-content: flex-start;
      width: 100%;
      padding: 0 0 20px;
      opacity: .5;
      transition: opacity .2s ease, transform .3s ease, visibility .3s ease;

      &.opened {
        visibility: visible;
        transform: translateX(0);
        opacity: 1;
      }
      .btn-login { order: 0; }
      > .ui-btn-text { font-weight: inherit; }
      &::v-deep .learn-collapsible {
        width: calc(100% - 40px);
        margin: -10px 20px 5px;

        .header .flex {
          font-size: inherit;
          font-weight: inherit;
        }
        .header .svg-icon {
          width: 10px;
          height: 10px;
        }
        .learn-drop-container { padding: 0; }
      }
    }
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';

import UButton from '@/components/ui/UButton.vue';
import UPopup from '@/components/ui/UPopup.vue';
import UDrop from '@/components/ui/UDrop.vue';
import UDivider from '@/components/ui/UDivider.vue';
import UCollapsible from '@/components/ui/UCollapsible.vue';
import AccountInfo from '@/components/Account/info.vue';
import SearchComponent from '@/components/Search/SearchComponent.vue';
import AccountStore from '@/models/Account';

const defferedActionName = 'ofirio-deffered-upgrade-action';

export default defineComponent({
  components: {
    SearchComponent,
    UCollapsible,
    AccountInfo,
    UDrop,
    UDivider,
    UButton
  },
  data() {
    return {
      mobileMenuOpened: false
    }
  },
  methods: {
    authComponentReset(state:boolean) {
      if (state == false)
        (<any>this.$refs.authComponent).reset(300);
    },
    toggleMobileMenu(forceState?:boolean) {
      this.mobileMenuOpened = forceState != undefined ? forceState : !this.mobileMenuOpened;
      document.body.classList.toggle('no-scroll', this.mobileMenuOpened);

      if (!this.mobileMenuOpened)
        return;

      const rightMenu = <any>this.$refs.rightMenu;
      rightMenu.scrollTop = -rightMenu.scrollHeight + rightMenu.offsetHeight;
    },
    onRegisterClick() {
      localStorage.setItem(defferedActionName, 'true');
      return (<any>this.$root)['ev-popup-login-open']('register');
    }
  },
  computed: {
    Account() { return AccountStore; }
  }
})
</script>