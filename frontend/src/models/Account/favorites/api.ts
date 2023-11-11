import axios from 'axios';
import { of } from 'await-of';

export type TAccountDTO__FavoriteItem = {
  prop_id: string,
  added_time: string,
  is_available: boolean,
  photo1: string,
  address: string,
  price: number,
  beds: number,
  baths: number,
  building_size: number,
  cash_on_cash: number,
  cap_rate: number,
  total_return: number,
  predicted_rent: number
}

export type TAccountDTO__FavoritesList = {
  items: Array<TAccountDTO__FavoriteItem>
}

export type TAccountDTO__FavoritesQty = {
  qty: number
}

export default {
  loadFavoritesList: function () {
    return <AxiosRequestToAwaiting<TAccountDTO__FavoritesList>>of(axios.get(`/api/account/favorites`));
  },
  getFavoritesQty: function () {
    return <AxiosRequestToAwaiting<TAccountDTO__FavoritesQty>>of(axios.get(`/api/account/favorites_qty`));
  }
}