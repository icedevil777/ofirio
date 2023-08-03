<template>
<div class="viewbox flex" v-if="Account.Basis.isLoggedIn">
  <div class="sub-menu">
    <AccountInfo class="hide-mobile" />
    <UDivider class="hide-mobile" />
    <div class="sub-links">
      <router-link to="/account/subscription" class="sub-router-link">
        <span class="icon-wrapper">
          <UIcon name="arrow-in-circle"/>
        </span>
        <span class="hide-mobile">Subscription</span>
        <span class="hide-desktop">Update</span>
      </router-link>
      <router-link to="/account/favorites" class="sub-router-link">
        <span class="icon-wrapper">
          <UIcon name="heart"/>
        </span>
        <span>Favorites</span>
      </router-link>
      <router-link to="/account/reports" class="sub-router-link">
        <span class="icon-wrapper">
          <UIcon name="plot-up" class="nofill"/>
        </span>
        <span>Reports</span>
      </router-link>
      <router-link to="/account/settings" class="sub-router-link">
        <span class="icon-wrapper">
          <UIcon name="gear" class="nofill"/>
        </span>
        <span class="hide-mobile">Account settings</span>
        <span class="hide-desktop">Settings</span>
      </router-link>
      <!-- <router-link to="/account/favorites1" class="sub-router-link"><UIcon name="list-magnifier"/>Saved Searches</router-link> -->
      <router-link to="/account/email-settings" class="sub-router-link">
        <span class="icon-wrapper">
          <UIcon name="mail-setup" />
        </span>
        <span class="hide-mobile">Email settings</span>
        <span class="hide-desktop">Emails</span>
      </router-link>
      <span class="sub-router-link hide-mobile" @click="Account.Auth.logout()">Log Out</span>
    </div>
  </div>
  <div class="sub-view">
    <router-view></router-view>
  </div>
</div>
</template>

<style lang="less" scoped>
.viewbox {
  height: calc(100vh - @header-height);
  justify-content: stretch;
  align-content: flex-start;
  align-items: flex-start;

  > div { height: 100%; }
  .sub-menu {
    @p: 30px;
    @mh: 60px;

    width: 25%;
    max-width: 300px;
    background-color: @col-bg;
    position: relative;
    box-shadow: 0px 0px 30px @col-shadow;

    .account-info {
      padding: @p @p 0 @p;

      &::v-deep > .ui-button {
        margin-top: 10px;
        font-size: 0.85rem;
      }
    }
    .ui-divider {
      width: calc(100% - 2*@p);
      margin: @p auto;
    }
    .sub-links {
      padding-left: @p;

      .sub-router-link {
        @h: 44px;
        
        display: block;
        position: relative;
        padding-left: @p * 2;
        height: @h;
        line-height: @h;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        color: @col-text-gray-darker;
        font-weight: 700;
        border-right: 5px solid transparent;
        margin-bottom: 15px;
        cursor: pointer;

        &.router-link-active {
          border-right-color: @col-green;
          color: @col-text-dark;

          .icon-wrapper {
            background: fade(@col-green, 10%);

            @media @mobile { background: transparent; }
          }

          .svg-icon {
            fill: @col-green;

            &.nofill {
              fill: transparent;
              stroke: @col-green;
            }
            @media @mobile { background: transparent; }
          }
        }
        .icon-wrapper {
          @s: 44px;
          width: @s;
          height: @s;
          position: absolute;
          border-radius: 50%;
          vertical-align: middle;
          margin-right: 16px;
          display: inline-block;
          left: 0;

          @media @mobile {
            position: static;
            margin: 0 0 0;
            text-align: center;
            height: 20px;
          }
        }
        &:hover .icon-wrapper { 
          background: fade(@col-green, 10%); 
          @media @mobile { background: transparent; }
        }
        .svg-icon {
          @s: 20px;
          position: absolute;
          left: calc(@h/2 - @s/2);
          top: calc(@h/2 - @s/2);
          width: @s;
          height: @s;
          fill: @col-text-gray-darker;
          box-sizing: content-box;

          &.nofill {
            fill: transparent;
            stroke: @col-text-gray-darker;
            // workaround with svgo
            stroke-width: 2;
          }

          @media @mobile {
            position: static;
            min-width: @s;
            min-height: @s;
            padding: 0;
          }
        }

        @media @mobile {
          height: @mh;
          padding: 0;
          border: none;
          display: flex;
          flex-direction: column;
          justify-content: space-evenly;
          align-items: center;
          align-content: center;
          text-transform: uppercase;

          span {
            height: auto;
            display: block;
            font-size: .75rem;
            line-height: 1rem;
          }
        }
      }

      @media @mobile {
        display: flex;
        justify-content: space-evenly;
        align-items: flex-end;
        padding: 0 5px;
      }
    }

    @media @mobile {
      position: fixed;
      bottom: 0;
      left: 0;
      width: 100%;
      z-index: 5;
      max-width: none;
      height: @mh;
      padding: 0;
    }
  }
  .sub-view {
    background: #F5F7FB;
    flex: 1;
    overflow-y: auto;
  }
}
::v-deep {
  .account-internal-padding {
    padding: 0 50px;
    margin: 50px 0;

    > h1.heading {
      font-weight: 800;
      font-size: 2.25rem;
      display: block;
      margin-bottom: 40px;
    }
    .account-sub-block {
      background: @col-bg;
      padding: 30px 40px;
      border-radius: @border-radius;
      position: relative;

      span, p {
        display: block;
      }
      .ui-table {
        width: 100%;

        .ui-href {
          font-weight: 800;
          font-size: .875rem;
          text-transform: uppercase;
        }
      }
      .sub-heading {
        display: block;
        font-size: 1.875rem;
        margin-bottom: 1.5rem;
        font-weight: 700;
      }

      @media @mobile { padding: 20px; }
    }

    @media @mobile {
      padding: 0 20px;
      margin: 20px 0 70px;
    }
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';
import AccountInfo from '@/components/Account/info.vue';
import UDivider from '@/components/ui/UDivider.vue';

import AccountStore from '@/models/Account';

export default defineComponent({
  components: {
    AccountInfo,
    UDivider
  },
  computed: {
    Account: function() {
      return AccountStore;
    }
  }
})
</script>