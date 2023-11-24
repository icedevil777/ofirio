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

let getUrl = ''
if (location.hostname === 'localhost') {
  getUrl = 'https://localhost'
}

export default {
  loadEmailSettings: function () {
    return <AxiosRequestToAwaiting<TAccountDTO__EmailSettings>>of(axios.get(`${getUrl}/api/account/email_settings`));
  },
  setEmailSettings: function (data: TAccountDTO__EmailSettings) {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`${getUrl}/api/account/email_settings`, data));
  }
}