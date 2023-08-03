<template>
  <div class="unlock-analytics flex" :class="{ 'transparant': mode != 'default' }" @click="unlockAction">
    <UIcon v-if="mode == 'default'" name="lock-warning" />
    <UIcon v-else-if="mode == 'simple'" name="lock" />
    <UButton class="ui-href" :class="{ 'ui-href-underline': mode == 'default', 'ui-href-default': mode == 'simple' }">
      <slot>Unlock Analytics</slot>
    </UButton>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import UButton from '@/components/ui/UButton.vue'
import AccountStore from '@/models/Account';

const defferedActionName = 'ofirio-deffered-upgrade-action';

export default defineComponent({
  props: {
    mode: { type: String, default: 'default' }
  },
  components: {
    UButton
  },
  computed: {
    Account() {
      return AccountStore;
    }
  },
  methods: {
    unlockAction() {
      const root = (<any>this.$root);

      if (AccountStore.Basis.isLoggedIn)
        return root.$refs.popupUpgrade.open();

      localStorage.setItem(defferedActionName, 'true');
      return root['ev-popup-login-open']('register');
    }
  },
  mounted() {
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
})
</script>

<style lang="less" scoped>
  .unlock-analytics {
    justify-content: center;
    align-items: center;
    align-content: center;
    flex-wrap: wrap;
    cursor: pointer;
    padding: 0.5rem 1rem;
    background: #F0EEF9;
    border-radius: @border-radius;
    text-align: center;
    
    &.transparant { background: transparent; }
  }
  .ui-href {
    font-weight: 700;
    line-height: 1.25rem;
  }
  .svg-icon {
    @s: 20px;
    width: @s;
    height: @s;
    fill: @col-text-gray-darker;
    flex-shrink: 0;

    @media @mobile {
      width: @s*0.8;
      height: @s*0.8;
    }
  }
</style>
