import { AccountStoreType } from '@/models/Account';

import API, { TAccountDTO__EmailSettings } from './api';
import VueStore from 'vue-class-store';
import { APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED } from '@/constants/DefaultMessages';

let Account: AccountStoreType;

@VueStore
export default class AccountEmailSettingsModule {

  private _dto: TAccountDTO__EmailSettings | null = null;

  constructor(AccountRef: AccountStoreType) {
    Account = AccountRef;
  }

  public get dto() {
    return this._dto;
  }

  public async load() {

    this._dto = null;
    const [res, err] = await API.loadEmailSettings();

    if (err) {
      if (![401].includes(<number>err.response?.status)) {
        console.error('Account:EmailSettings :: Invalid response code');
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

  public async save() {
    if (!this._dto)
      return;

    const [res, err] = await API.setEmailSettings(this._dto);

    if (err) {
      if (![401].includes(<number>err.response?.status)) {
        console.error('Account:EmailSettings :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
      }
      
      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return false;
    }

    return true;
  }

}