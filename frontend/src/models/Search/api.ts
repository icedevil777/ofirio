import { HiddenSearchResult, SearchResult, TSearchResults } from '@/models/Search/index';
import axios from 'axios';
import { of } from 'await-of';


type TSearchRequest__TypeProps = {
  state_id: string,
  county: string,
  city: string,
  zip: string,
  geo_polygons?: string
}

type TSearchRequest__StateId = {
  type: 'state'
} & Pick<TSearchRequest__TypeProps, 'state_id'>

type TSearchRequest__County = {
  type: 'county'
} & Pick<TSearchRequest__TypeProps, 'state_id' | 'county'>

type TSearchRequest__City = {
  type: 'city'
} & Pick<TSearchRequest__TypeProps, 'state_id' | 'county' | 'city'>

type TSearchRequest__Zip = {
  type: 'zip'
} & Pick<TSearchRequest__TypeProps, 'zip'>

type TSearchRequest__Geo = {
  type: 'geo'
} & Pick<TSearchRequest__TypeProps, 'geo_polygons'>

type TSearchElasticResponse__Property = {
  type: 'address',
  prop_id: string
}

export type TSearchRequest__Type = TSearchRequest__StateId | TSearchRequest__County | TSearchRequest__City | TSearchRequest__Zip | TSearchRequest__Geo;
export type TSearchElasticResponse__Type = TSearchRequest__StateId | TSearchRequest__County | TSearchRequest__City | TSearchRequest__Zip | TSearchElasticResponse__Property;

export type TSearchRequest__Filters = {
  cap_rate_min?: number,
  cash_on_cash_min?: number,
  prop_type2?: 'condo-apt' | 'house-duplex',
  predicted_rent_min?: number,
  price_min?: number,
  price_max?: number,
  beds_min?: number,
  beds_max?: number,
  baths_min?: number,
  year_built_min?: number,
  year_built_max?: number,
  build_size_min?: number,
  build_size_max?: number,
  status_for_sale?: boolean,
  status_pending?: boolean,
  status_sold?: boolean,
  is_55_plus?: boolean,
  is_rehab?: boolean,
  is_cash_only?: boolean,
  is_good_deal?: boolean,
  hide_is_55_plus?: boolean,
  hide_is_rehab?: boolean,
  hide_is_cash_only?: boolean
}

export type TSearchRequest__Sort = {
  sort_field?: 'price' | 'predicted_rent' | 'year_built' | 'cap_rate' | 'list_date' | 'update_date'
  sort_direction?: 'asc' | 'desc'
}

export type TSearchRequest__Options = {
  map_query?: boolean,
  start: number,
  viewport?: string,
  zoom?: number,
  map_height?: number,
  map_width?: number
}

export type TSearchRequest = TSearchRequest__Options & TSearchRequest__Type & TSearchRequest__Filters & TSearchRequest__Sort;



export type TSearchRequest__RecalcProperty = {
  prop_id: string,
  price: number,
  market_rent: number
}
export type TSearchRequest__RecalcMortage = {
  down_payment: number,
  financing_years: number,
  interest_rate: number,
  prop_details: Array<TSearchRequest__RecalcProperty>
}

export type TSearchRequest__RecalcMortageRow = {
  prop_id: string,
  cash_on_cash: number,
  total_return: number
}

export type TSearchRequest__RecalcMortageResult = {
  result: Array<TSearchRequest__RecalcMortageRow>
}

type TSearchSuggestionQuery = {
  query: string
}
export type TSearchSuggestion = TSearchElasticResponse__Type & { label: string }
export type TSearchSuggestionResult = {
  items: Array<TSearchSuggestion>
}

export type TSearchSuggestionRectResult = {
  rect: string
}

export type TSearchResults__Server = Omit<TSearchResults, 'map'> & { map: { items: Array<HiddenSearchResult|SearchResult> } };

export default {
  search: function (data:TSearchRequest) {
    console.log('data:TSearchRequest', data)
    return <AxiosRequestToAwaiting<TSearchResults__Server>>of(axios.post('/api/search', data));
  },

  recalc: function (data:TSearchRequest__RecalcMortage) {
    return <AxiosRequestToAwaiting<TSearchRequest__RecalcMortageResult>>of(axios.post('/api/search/mortgage', data));
  },

  elasticQuery: function (data:TSearchSuggestionQuery) {
    return <AxiosRequestToAwaiting<TSearchSuggestionResult>>of(axios.post('/api/search/autocomplete', data));
  },

  rectQuery: function (data: TSearchSuggestionQuery) {
    return <AxiosRequestToAwaiting<TSearchSuggestionRectResult>>of(axios.post(`/api/search/address-rect`, data));
  }
}