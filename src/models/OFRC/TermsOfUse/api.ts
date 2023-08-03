import axios from 'axios';
import { of } from 'await-of';

export type TTermsOfUse_Update_Onsite = {
  broward: Date,
  matrix: Date,
  miami: Date,
  stellar: Date
}
export type TTermsOfUse_Mls_Info = {
  update_onsite: TTermsOfUse_Update_Onsite
}

export default {
  getMlsInfo: function () {
    return  <AxiosRequestToAwaiting<TTermsOfUse_Mls_Info>>of(axios.get('/api/mls_info'));
  }
}