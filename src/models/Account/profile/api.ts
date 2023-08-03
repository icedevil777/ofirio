import axios from 'axios';
import { of } from 'await-of';

type TAccountDTO__Client_UpdateBasicInfo = {
  first_name: string,
  last_name: string
}

export default {
  updateBasicInfo: function (data:TAccountDTO__Client_UpdateBasicInfo) {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`/api/account/change_profile`, data));
  },
  acceptTermsOfUse: function () {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`/api/account/accept_terms_of_use`));
  }
}