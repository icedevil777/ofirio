<template>
  <div class="ofirio-cookie flex" :class="{ 'active': cookieAskContest }" data-nosnippet>
    <span>
      We use <b>cookies</b> to improve your experience on our site and to analyse our traffic. To find out more read our
      <router-link :to="{ name: 'static-privacy-policy' }">
          <a @click="() => $root['ev-popup-login-close']()" class="ui-href ui-href-underline">Privacy Policy</a>
      </router-link>.
    </span>
    <div>
      <UButton class="ui-btn ui-btn-green" @click="cookieConfirmed">Got it</UButton>
      <UIcon @click="cookieConfirmed" name="cross"/>
    </div>
  </div>  
</template>

<style lang="less" scoped>
  .ofirio-cookie {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    transform: translateY(100%);
    z-index: 5000;
    opacity: 0;
    visibility: hidden;
    background: @col-bg;
    padding: 20px 30px;
    box-shadow: 0px -1px 12px @col-shadow;
    transition: transform .2s ease, opacity .3s ease, visibility .3s ease;
    justify-content: space-between;
    align-items: center;
    
    &.active {
      transform: translateY(0);
      opacity: 1;
      visibility: visible;
    }

    span {
      line-height: 1.25rem;

      b { font-weight: 700; }
    }
    .ui-button { white-space: nowrap; }
    .svg-icon {
      @s: 0.85rem;
      width: @s;
      height: @s;
      fill: @col-text-on-disabled;
      margin-left: 20px;
      cursor: pointer;

      @media @mobile {
        position: absolute;
        right: 8px;
        top: 8px;
      }
    }

    @media @mobile {
      display: block;
      padding: 20px;

      .ui-btn {
        display: block;
        margin-top: 20px;
        width: 100%;
      }
    }
  }
</style>

<script lang="ts">
import { defineComponent } from 'vue';

import UButton from '@/components/ui/UButton.vue';

const LOCALSTORAGE_COOKIE_KEYNAME = 'ofirio-cookie-contest-asked';

export default defineComponent({
  components: {
    UButton,
  },
  data() {
    return {
      cookieAskContest: false
    }
  },
  methods: {
    cookieConfirmed() {
      window.localStorage.setItem(LOCALSTORAGE_COOKIE_KEYNAME, 'true');
      this.cookieAskContest = false;
    }
  },
  mounted() {
    const cookieAsk = window.localStorage.getItem(LOCALSTORAGE_COOKIE_KEYNAME);
    if (!cookieAsk)
      this.cookieAskContest = true;
  }
})
</script>
