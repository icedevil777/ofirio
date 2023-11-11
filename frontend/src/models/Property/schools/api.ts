import axios from 'axios';
import { of } from 'await-of';
import { TPropertyDTO_Schools } from '@/models/Property/schools';

type TPropertyDTO__Client_PropertyId = {
  prop_id: string
}


export default {
  calculate: function (data:TPropertyDTO__Client_PropertyId) {
    return <AxiosRequestToAwaiting<TPropertyDTO_Schools>>of(axios.post(`/api/property/schools`, data));
  }
}