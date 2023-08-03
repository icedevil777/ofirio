import axios from 'axios';
import { of } from 'await-of';
import { TPropertyDTO_Taxes } from '@/models/Property/taxes';

type TPropertyDTO__Client_PropertyId = {
  prop_id: string
}

export default {
  calculate: function (data:TPropertyDTO__Client_PropertyId) {
    return <AxiosRequestToAwaiting<TPropertyDTO_Taxes>>of(axios.post(`/api/property/tax_history`, data));
  }
}