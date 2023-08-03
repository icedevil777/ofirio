import API from './api';
import VueStore from 'vue-class-store';

export type TPropertyTaxRow = {
  tax: number,
  year: string,
  assessment: {
    land: number,
    total: number,
    building: number
  }
}
export type TPropertyDTO_Taxes = {
  tax_history: Array<TPropertyTaxRow>
}

@VueStore
export default class PropertyTaxModel {

  private _dto: TPropertyDTO_Taxes | null = null;
  constructor () {}

  public async init(id: string) {
    const [res, err] = await API.calculate({ prop_id: id });

    if (err) {
      if (![200, 400, 404].includes(<number>err.response?.status))
        console.error('Property:Taxes :: Invalid response code');
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