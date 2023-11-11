import axios from 'axios';
import { of } from 'await-of';
import { TPropertyDTO_History } from '@/models/Property/history';

type TPropertyDTO__Client_PropertyId = {
  prop_id: string
}

export default {
  calculate: function (data:TPropertyDTO__Client_PropertyId) {
    return <AxiosRequestToAwaiting<TPropertyDTO_History>>of(axios.post(`/api/property/prop_history`, data));
  }
}