<template>
  <div class="account-internal-padding email-settings">
    <h1 class="heading">Email settings</h1>

    <div class="account-sub-block">
      <span class="sub-heading">Alerts</span>
      <div class="alert-row flex">
        <span class="name">City Alerts</span>
        <UPreloader v-if="Account.EmailSettings.dto === null" mode="emailSettings" :activation="true" :width="15" />
        <UToggle v-else v-model="Account.EmailSettings.dto.alerts_city"/>
      </div>
      <div class="alert-row flex">
        <span class="name">Property alerts based on my criteria</span>
        <UPreloader v-if="Account.EmailSettings.dto === null" mode="emailSettings" :activation="true" :width="15" />
        <UToggle v-else v-model="Account.EmailSettings.dto.alerts_property" />
      </div>
    </div>

    <div class="account-sub-block">
      <span class="sub-heading">Comunications</span>
      <div class="alert-row flex">
        <span class="name">Promotions</span>
        <UPreloader v-if="Account.EmailSettings.dto === null" mode="emailSettings" :activation="true" :width="15" />
        <UToggle v-else v-model="Account.EmailSettings.dto.comm_promotions" />
      </div>
      <div class="alert-row flex">
        <span class="name">Monthly Newsletter</span>
        <UPreloader v-if="Account.EmailSettings.dto === null" mode="emailSettings" :activation="true" :width="15" />
        <UToggle v-else v-model="Account.EmailSettings.dto.comm_monthly_newsletters" />
      </div>
      <div class="alert-row flex">
        <span class="name">Tips &amp; Blogs</span>
        <UPreloader v-if="Account.EmailSettings.dto === null" mode="emailSettings" :activation="true" :width="15" />
        <UToggle v-else v-model="Account.EmailSettings.dto.comm_tips_blogs" />
      </div>
      <div class="alert-row flex">
        <span class="name">Product Updates</span>
        <UPreloader v-if="Account.EmailSettings.dto === null" mode="emailSettings" :activation="true" :width="15" />
        <UToggle v-else v-model="Account.EmailSettings.dto.comm_product_updates" />
      </div>
    </div>

    <UButton class="ui-btn ui-btn-green" @click="Account.EmailSettings.save">Update</UButton>
  </div>
</template>

<style lang="less" scoped>
.email-settings {
  .account-sub-block {
   
    .sub-heading { font-weight: 800; }
    & + .account-sub-block { margin-top: 40px; }
  }
  .alert-row {
    width: 100%;
    justify-content: space-between;
    align-items: center;
    padding: 25px 0;
    line-height: 1.4rem;

    & + .alert-row {
      border-top: 1px solid @col-gray;
    }
    .ui-toggle {
      margin-left: 1rem;

      @media @mobile {
        &::v-deep .label { display: none; }
      }
    }
  }
  > .ui-btn-green {
    width: 100%;
    max-width: 400px;
    height: 50px;
    margin-top: 40px;
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';

import UButton from '@/components/ui/UButton.vue';
import UToggle from '@/components/ui/UToggle.vue';
import UPreloader from '@/components/ui/UPreloader.vue';
import AccountStore from '@/models/Account';
import { TAccountDTO__EmailSettings } from '@/models/Account/email-settings/api';

export default defineComponent({
  components: {
    UButton,
    UToggle,
    UPreloader
  },
  computed: {
    Account() {
      return AccountStore;
    }
  },
  setup() {
    AccountStore.EmailSettings.load();
  }
})
</script>