<template>
  <template v-if="accountTypeName">
    <span class="account-label" :class="[ 'account-label--' + accountTypeName.class ]">{{ accountTypeName.text }}</span>
  </template>
</template>

<style lang="less" scoped>
  .account-label {
    @h: 18px;

    padding: 0 5px;
    height: @h;
    line-height: @h - 2px;
    font-size: 0.625rem;
    font-weight: 800;
    border: 1px solid @col-green-light;
    border-radius: 4px;
    text-transform: uppercase;

    @media @mobile { font-size: 0.8rem; }

    &.account-label--account-free {
      border-color: @col-text-gray-dark;
      color: @col-text-gray-dark;
    }
    &.account-label--account-free {
      color: @col-text-on-disabled;
      border: 1px solid @col-text-on-disabled;
    }
    &.account-label--account-unverified {
      color: @col-text-light;
      background: @col-warn;
    }
    &.account-label--account-premium {
      color: @col-green;
      background: rgba(1, 208, 146, 0.1);
    }
  }

</style>

<script lang="ts">
import { defineComponent } from 'vue';
import AccountStore from '@/models/Account';

export default defineComponent({
  computed: {
    accountTypeName() {
      if (!AccountStore.Auth.inited)
        return undefined;

      if (!AccountStore.Auth.isLoggedIn || !AccountStore.Basis.dto)
        return undefined;
        
      if (!AccountStore.Basis.dto.verified)
        return { class: 'account-unverified', text: 'Unverified Account' };

      if (AccountStore.Basis.dto.access_status == 'verified')
        return { class: 'account-free', text: 'Free Account' };

      if (AccountStore.Basis.dto.access_status == 'trial' || AccountStore.Basis.dto.access_status == 'premium')
        return { class: 'account-premium', text: 'Premium Account' };

      return undefined;
    }
  }
});
</script>