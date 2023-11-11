import API from './api';
import VueStore from 'vue-class-store';

type TProperty_HistoryRow = {
  date: string,
  sqft: number,
  price: number,
  source: string,
  event_name: string,
  price_changed: number,
  datasource_name: string,
  price_range_max: null | number,
  price_range_min: null | number
}
export type TPropertyDTO_History = {
  prop_history: Array<TProperty_HistoryRow>
}

@VueStore
export default class PropertyHistoryModel {

  private _dto: TPropertyDTO_History | null = null;
  constructor () {}

  public async init(id: string) {
    const [res, err] = await API.calculate({ prop_id: id });

    if (err) {
      if (![200, 400, 404].includes(<number>err.response?.status))
        console.error('Property:History :: Invalid response code');
      this._dto = null;
      return false;
    }

    this._dto = res.data;
    return true;
  }

  public get dto() {
    return this._dto;
  }

}