import ReportsAPI, { TReportDTO__ListItem } from '@/models/Reports/api';
import { AccountStoreType } from '@/models/Account';
import VueStore from 'vue-class-store';
import { APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED } from '@/constants/DefaultMessages';

let Account: AccountStoreType;

@VueStore
export default class AccountReportsModule {

  private _dto: TReportDTO__ListItem[] | null = null;

  constructor(AccountRef: AccountStoreType) {
    Account = AccountRef;
  }

  public get dto() {
    return this._dto;
  }

  public async load() {

    this._dto = null;
    const [res, err] = await ReportsAPI.loadReportsList();

    if (err) {
      if (![401].includes(<number>err.response?.status)) {
        console.error('Account:Reports :: Invalid response code');
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

}