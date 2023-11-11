import { TAccountBaseDTO } from '@/models/Account/basis';
import { AccountStoreType } from '@/models/Account';
import profileApi from './api';
import VueStore from 'vue-class-store';
import { APP_DEFAULT_SMTH_BAD_FROM_SERVER, APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED } from '@/constants/DefaultMessages';

let Account: AccountStoreType;

@VueStore
export default class AccountProfileModule {

  private _dto: TAccountBaseDTO | null = null;

  constructor(AccountRef: AccountStoreType) {
    Account = AccountRef;
  }

  public get dto() {
    return this._dto;
  }

  public setDTO(dto: TAccountBaseDTO | null) {
    this._dto = dto;
  }

  public async update(first_name: string, last_name: string) {
    const [res, err] = await profileApi.updateBasicInfo({ first_name, last_name });

    if (err) {
      if (err.response?.status != 400) {
        console.error('Account:Profile :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
      }
      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return false;
    }

    Account.Auth.loadAccountDTO();
    return true;
  }

  public async acceptTermsOfUse() {
    if (!Account.Auth.isLoggedIn)
      return;
      
    const [res, err] = await profileApi.acceptTermsOfUse();

    if (err)
      throw APP_DEFAULT_SMTH_BAD_FROM_SERVER;
    
    this.dto?.warnings?.splice(this.dto?.warnings?.indexOf('terms_of_use_not_accepted'), 1);
    return true;
  }

}