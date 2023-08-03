import axios from 'axios';
import { of } from 'await-of';
import { TPropertyDTO_Basis } from '@/models/Property/basis';

export type TPropertyDTO__Client_PropertyId = {
  prop_id: string
}

export type TPropertyCallAgents__Client_Request = {
  full_name: string,
  email: string,
  phone: string,
  request: string,
  prop_id: string
}

export type TPropertyMarkFavorite__Client_Request = {
  prop_id: string
}

export default {
  getBasis: function (data:TPropertyDTO__Client_PropertyId) {
    return <AxiosRequestToAwaiting<TPropertyDTO_Basis>>of(axios.post(`/api/property`, data));
  },
  callAgents: function (data:TPropertyCallAgents__Client_Request) {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`/api/property/contact_agent`, data));
  },
  addFavorite: function (data: TPropertyMarkFavorite__Client_Request) {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`/api/property/favorite`, { action: 'create', ...data }));
  },
  removeFavorite: function (data: TPropertyMarkFavorite__Client_Request) {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`/api/property/favorite`, { action: 'delete', ...data }));
  }
}