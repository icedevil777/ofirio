import { AccountStoreType } from '@/models/Account';

import API, { TAccountDTO__FavoritesList } from './api';
import VueStore from 'vue-class-store';
import { APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED } from '@/constants/DefaultMessages';

let Account: AccountStoreType;

@VueStore
export default class AccountFavoritesModule {

  private _dto: TAccountDTO__FavoritesList | null = null;

  constructor(AccountRef: AccountStoreType) {
    Account = AccountRef;
  }

  public get dto() {
    return this._dto;
  }

  public async load() {

    this._dto = null;
    const [res, err] = await API.loadFavoritesList();

    if (err) {
      if (err.response?.status != 401) {
        console.error('Account:Favorites :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
      }
      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return false;
    }

    this._dto = res.data;
    return true;
  }

  public async getQty() {
    if (Account.Basis.dto == null)
      return 0;

    const [res, err] = await API.getFavoritesQty();

    if (err) {
      if (err.response?.status != 401) {
        console.error('Account:Favorites :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
      }
      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return NaN;
    }
    
    Account.Basis.dto.favorites_qty = res.data.qty;
    return res.data.qty;
  }

}