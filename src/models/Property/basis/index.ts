import API, { TPropertyCallAgents__Client_Request } from './api';
import VueStore from 'vue-class-store';
import { SearchResult } from '@/models/Search';
import { TAccountDTO__FavoriteItem } from '@/models/Account/favorites/api';
import AccountStore from '@/models/Account';
import { observe, sendEvent } from '@/services/LocalstorageWatcher.service';
import ReportAPI from '@/models/Reports/api';

export type TPropertyDTO_Basis = {
  data: {
    beds: number,
    baths: number,
    price: number,
    garage: string,
    hoa_fees: number,
    year_built: number,
    description: string,
    monthly_tax: number,
    building_size: number,
    predicted_rent: number,
    monthly_insurance: number,
    median: number,
    min_range_rent: number,
    max_range_rent: number,
    price_per_sqft: number,
    is_mls: boolean,
    mls_type: 'stellar' | 'miami' | 'broward' | 'matrix'
  },
  address: {
    lat: number,
    lon: number,
    zip: string,
    city: string,
    line: string,
    state: string,
    county: string,
    state_code: string
  },
  favorite: boolean,
  photos: Array<string>,
  summary: {
    baths: number,
    beds: number,
    building_size: number,
    garage: string,
    hoa_fees: number,
    last_price: number,
    last_sold_date: string,
    last_sold_price: number,
    monthly_insurance: number,
    monthly_tax: number,
    pool: string,
    price_per_sqft: number,
    prop_type: string,
    status: string,
    year_built: number
  },
  mls_info: {
    mls_number?: string,
    association?: string,
    listing_office?: string,
    association_fee?: string,
    originating_mls?: string
  },
  features: Record<string, Record<string, Record<string, string> | string>>,
  public_records?: Record<string, number | string>,
  status: 'for_sale' | 'pending' | 'sold',
  badges: Array<string>,
  update_date: string,
  update_onsite: string,
  prediction_quality: 'low' | 'medium' | 'high',
  is_55_plus: boolean,
  is_rehab: boolean,
  is_cash_only: boolean
}


@VueStore
export default class PropertyBasisModule {

  private id: string | null = null;
  private _dto: TPropertyDTO_Basis | null = null;

  constructor () {}

  public async init(id: string) {
    this.id = null;
    const [res, err] = await API.getBasis({ prop_id: id });

    if (err) {
      if (![200, 400, 404].includes(<number>err.response?.status))
        console.error('Property:Basis :: Invalid response code');
      this._dto = null;
      return false;
    }

    this._dto = res.data;
    this.id = id;

    observe('ofirio-favorite-added', (upd_id:string) => {
      if (upd_id == id && this._dto)
        this._dto.favorite = true;
    });
    observe('ofirio-favorite-removed', (upd_id:string) => {
      if (upd_id == id && this._dto)
        this._dto.favorite = false;
    });
    return true;
  }

  public get dto() {
    return this._dto;
  }

  public getId() {
    return this.id;
  }

  public async generateReport(options?: any) {
    if (!this.id)
      return;
    
    const [res, err] = await ReportAPI.reportProperty({ prop_id: this.id, ...options, monthly_rent: Math.round(options.monthly_rent) });

    if (err) {
      if (![401].includes(<number>err.response?.status))
        console.error('Property:Report :: Invalid response code');
      return;
    }

    return res.data;
  }

}

export async function callAgents(data: TPropertyCallAgents__Client_Request) {
  if (!data.prop_id)
    return;

  const [res, err] = await API.callAgents(data);
  if (err) {
    if (![200, 400, 404].includes(<number>err.response?.status))
      console.error('Property:callAgents :: Invalid response code');
    return false;
  }
  return true;
}

export async function markFavorite(property: PropertyBasisModule | SearchResult | TAccountDTO__FavoriteItem, setAs: boolean = true) {
  
  const id = (<SearchResult>property).prop_id || (<PropertyBasisModule>property).getId();

  if (!id)
    return false;

  let res, err;

  if (setAs)
    [res, err] = await API.addFavorite({ prop_id: id });
  else
    [res, err] = await API.removeFavorite({ prop_id: id });

  if (err) {
    if (![200, 400, 404].includes(<number>err.response?.status))
      console.error('Property:markFavorite :: Invalid response code');
    return false;
  }
  
  if ((<PropertyBasisModule>property).dto?.favorite != undefined)
    //@ts-ignore
    property.dto.favorite = setAs;

  else if ((<SearchResult>property).favorite != undefined)
    //@ts-ignore
    property.favorite = setAs;
  
  if (AccountStore.Basis.dto) {
    setAs ? AccountStore.Basis.dto.favorites_qty++ : AccountStore.Basis.dto.favorites_qty--;
    sendEvent(setAs ? 'ofirio-favorite-added' : 'ofirio-favorite-removed', id);
  }
  return true;
}