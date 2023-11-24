import { AccountStoreType } from '@/models/Account';
import { observe } from '@/services/LocalstorageWatcher.service';
import VueStore from 'vue-class-store';

export type TAccountBaseDTO = {
  access_status: 'free' | 'trial' | 'premium' | 'verified',
  email: string,
  favorites_qty: number,
  first_name: string,
  is_admin: boolean,
  is_team: boolean,
  last_name: string,
  pk: number,
  subscription: TAccountBaseDTO__SubscriptionInfo,
  verified: boolean,
  warnings: Array<TAccountBaseDTO__Warnings>
}

export type TAccountBaseDTO__SubscriptionInfo = {
  cancel_at_period_end: boolean,
  paid_by: string,
  period: 'month' | 'quarter' | 'year',
  plan: string,
  status: 'active' | 'past_due' | 'unpaid' | 'canceled' | 'incomplete' | 'incomplete_expired' | 'trialing'
}

export type TAccountBaseDTO__Warnings = 'terms_of_use_not_accepted' | 'change_password_requested';

let Account: AccountStoreType;

@VueStore
export default class AccountBasisModule {

  private _dto: TAccountBaseDTO | null = null;

  constructor(AccountRef: AccountStoreType) {
    Account = AccountRef;

    observe('ofirio-favorite-added', () => {
      if (Account.Basis.dto)
        Account.Basis.dto.favorites_qty++;
    });
    observe('ofirio-favorite-removed', (e:string) => {
      if (Account.Basis.dto)
        Account.Basis.dto.favorites_qty--;
    });
  }

  public get dto() {
    return this._dto;
  }

  public get isLoggedIn() {
    return !!(Account.Auth.isLoggedIn && this.dto);
  }

  public get isPremium() {
    if (Account.Basis?.dto?.subscription?.status == 'active' || Account.Basis.dto?.subscription?.status == 'trialing')
      return true;

    return false;
  }

  public setDTO(dto: TAccountBaseDTO | null) {
    this._dto = dto;
  }


}