import axios from 'axios';
import { of } from 'await-of';

export type TPublic__Client__ContactUs = {
  full_name: string,
  email: string,
  message: string
}

export default {
  send: function (data: TPublic__Client__ContactUs) {
    return <AxiosRequestToAwaiting<TPublic__Client__ContactUs>>of(axios.post(`/api/contact_us`, data));
  }
}