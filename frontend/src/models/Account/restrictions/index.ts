import { AccountStoreType } from '@/models/Account';
import { ComponentPublicInstance } from 'vue';
import VueStore from 'vue-class-store';
import { TAccountDTO__Client_Subscription_Periods } from '../payments/api';

let Account: AccountStoreType;

@VueStore
export default class AccountRestrictionsModule {

  $root:any = null;

  constructor(AccountRef: AccountStoreType) {
    Account = AccountRef;
  }

  register(root:any) {
    this.$root = root;
  }

  public get canLogin() {
    if (Account.Auth.isLoggedIn)
      return false;

    return true;
  }

  public canCreateAccount() {
    if (Account.Auth.isLoggedIn)
      return this.$root.$refs.globMessages.push({ message: `You've already created an account`, type: 'warning' });

    return true;
  }

  public canUseCustomization() {
    if (!Account.Auth.isLoggedIn) {
      this.$root['ev-popup-login-open']('register');
      return false;
    }

    if (!Account.Basis.isPremium) {
      this.$root.$refs.popupUpgrade.open();
      return false
    }

    return true;
  }

  public canSaveProperty() {
    if (!Account.Auth.isLoggedIn) {
      this.$root['ev-popup-login-open']('register');
      return false;
    }

    return true;
  }

  public canUpgrade() {
    if (!Account.Auth.isLoggedIn) {
      this.$root['ev-popup-login-open']('register');
      return false;
    }

    return true;
  }

  public canStartFreeTrial() {
    if (!Account.Auth.isLoggedIn) {
      return this.$root['ev-popup-login-open']('register');
    }

    if (Account.Basis.isPremium) {
      return this.$root.$refs.globMessages.push({ message: `You're already a Premium member`, type: 'warning' });
    }

    return true;
  }

  public canUpgradeWith(plan: TAccountDTO__Client_Subscription_Periods) {
    if (!this.$root)
      return false;
    
    if (!Account.Auth.isLoggedIn) {
      this.$root['ev-popup-login-open']('register');
      return false;
    }

    if (Account.Basis.isPremium) {
      if (!Account.Subscriptions.isPayable(plan))
        return this.$root.$refs.globMessages.push({ message: 'Unable to upgrade to this plan', type: 'warning' });

      if (this.$root.$refs.popupUpgrade.isOpen)
        return true;

      return this.$root.$refs.popupUpgrade.open();
    }

    return true;
  }
}