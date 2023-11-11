<template>
<div class="account-info">
  <span class="fullName" v-text="Account.Basis.dto?.first_name ? Account.Basis.dto?.first_name + ' ' + Account.Basis.dto?.last_name : 'Stranger'"></span>
  <span class="email" v-text="Account.Basis.dto?.email"></span>
  <AccountLabel />
  <UButton
    v-if="!Account.Basis.isPremium"
    @click="goToSubs"
    class="ui-btn ui-btn-blue"
  >Upgrade Account</UButton>
</div>
</template>

<style lang="less" scoped>
.account-info {

  span {
    display: block;
    margin-bottom: 7px;
  }
  .fullName { font-weight: 700; }
  .email {
    color: @col-text-gray-darker;
    font-size: 0.75rem;
  }
  .account-label {
    display: inline-block;
    margin: 7px 0 0;
  }
  .ui-btn {
    @h: 40px;

    height: @h;
    width: 100%;
    text-align: center;
    margin: 20px 0 0;
    box-shadow: none;
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';
import UButton from '@/components/ui/UButton.vue';
import AccountLabel from '@/components/Account/sub/AccountLabel.vue';
import AccountStore from '@/models/Account';

export default defineComponent({
  components: {
    UButton,
    AccountLabel
  },
  computed: {
    Account() {
      return AccountStore;
    }
  },
  props: {
    afterNavigate: Function
  },
  methods: {
    goToSubs() {
      this.$router.push('/account/subscription');
      if (this.afterNavigate)
        this.afterNavigate();
    }
  }
})
</script>