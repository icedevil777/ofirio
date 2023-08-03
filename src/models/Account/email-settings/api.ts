import axios from 'axios';
import { of } from 'await-of';

export type TAccountDTO__EmailSettings = {
  alerts_city: boolean,
  alerts_property: boolean,
  comm_promotions: boolean,
  comm_monthly_newsletters: boolean,
  comm_tips_blogs: boolean,
  comm_product_updates: boolean
}

export default {
  loadEmailSettings: function () {
    return <AxiosRequestToAwaiting<TAccountDTO__EmailSettings>>of(axios.get(`/api/account/email_settings`));
  },
  setEmailSettings: function (data: TAccountDTO__EmailSettings) {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`/api/account/email_settings`, data));
  }
}