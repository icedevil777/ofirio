

class OFRCSearchModel {

  // data

  constructor (initialUrl: string ) {

  }


}


/*import qs from 'query-string';
import { Ref, ref } from 'vue';
import AccountStore from '@/models/Account';
import API, { TSearchRequest, TSearchRequest__Filters, TSearchRequest__RecalcMortage, TSearchRequest__RecalcMortageRow, TSearchRequest__Sort } from './api2';

export type BasisSearchResult = {
  cash_on_cash: number,
  cash_on_cash_mortgage?: number,

  total_return: number,
  total_return_mortgage?: number,

  geo_point: {
    lat: number,
    lon: number
  }
};

export type HiddenSearchResult = BasisSearchResult & {
  hidden: true
};

export type SearchResult = BasisSearchResult & {
  hidden: false,
  prop_id: string,
  prop_type2: string,
  building_size: number,
  photo1: string,
  state_id: string,
  city: string,
  county_name: string,
  zip: string,
  address: string,
  price: number,
  beds: number,
  baths: number,
  year_built: number,
  predicted_rent: number,
  cap_rate: number,
  favorite: boolean,
  status: 'for_sale' | 'pending' | 'sold',
  badges: Array<string>,
  is_55_plus: boolean,
  is_rehab: boolean
};

export type TSearchResults = {
  mode: string,
  hidden_in_total: number,
  search: {
    total: number,
    start: number,
    items: Array<HiddenSearchResult|SearchResult>
  },
  map?: Record<string, Array<HiddenSearchResult|SearchResult>>
}

export type TSearchRoute = {
  typeOptions: string,
  options: string,
  sort: string
}

export const searchResults:Ref<null | TSearchResults> = ref(null);
export async function findProperties(params: TSearchRoute, offset: number, map_query: boolean = false, additionalOpts: any) {
  
  const defNUllResponse = {
    search: {
      start: 0,
      total: 0,
      items: []
    },
    hidden_in_total: 0,
    mode: 'premium',
    map: {}
  };


  const parsedSearchType = toObject(params.typeOptions);

  let type = null;
  if (parsedSearchType.zip != undefined)
    type = <'zip'>'zip';
  else if (parsedSearchType.geo_rect != undefined)
    type = <'geo'>'geo';
  else if (parsedSearchType.city != undefined)
    type = <'city'>'city';
  else if (parsedSearchType.county != undefined)
    type = <'county'>'county';
  else if (parsedSearchType.state_id != undefined)
    type = <'state'>'state';

  if (type == null)
    return searchResults.value = null;;

  const parsedSearchSorting = <TSearchRequest__Sort>toObject(params.sort);
  const parsedSearchOptions = <TSearchRequest__Filters>toObject(params.options);

  if (!AccountStore.Basis.isPremium) {
    parsedSearchOptions.cash_on_cash_min = undefined;
    parsedSearchOptions.cap_rate_min = undefined;
    parsedSearchOptions.predicted_rent_min = undefined;
  }


  let bounds;
  let zoomLevel;
  
  if (additionalOpts?.map) {
    bounds = additionalOpts.map.getBounds().toUrlValue();
    zoomLevel = additionalOpts.map.getZoom();
  }


  //@ts-ignore
  const query:TSearchRequest = {
    type,
    ...parsedSearchType,
    ...parsedSearchOptions,
    ...parsedSearchSorting,
    start: offset,
    map_query,
    viewport: bounds,
    zoom: zoomLevel
  }

  let [res, err] = await API.search(query);
  if (!err)
    if (res.data) {
      if (searchResults.value == null)
        searchResults.value = defNUllResponse;

      if (searchResults.value != null) {
        searchResults.value.search = res.data.search;
        searchResults.value.hidden_in_total = res.data.hidden_in_total;
        searchResults.value.mode = res.data.mode;

        if (map_query) {
          searchResults.value.map = {};
          
          res.data.map.items.forEach(p => {
            if (!searchResults?.value?.map)
              return;

            const coords = `${ p.geo_point.lat },${ p.geo_point.lon }`;
            if (searchResults.value.map[coords] == undefined)
              searchResults.value.map[coords] = [];

            searchResults.value.map[coords].push(p);
          });
        }
      }

      return searchResults.value;
    }

  return searchResults.value = defNUllResponse;
}

export async function recalculateByMortgage(properties: undefined | Array<HiddenSearchResult | SearchResult>, params: Omit<TSearchRequest__RecalcMortage, 'prop_details'>) {
  if (properties == undefined)
    return;

  const filteredProps = <SearchResult[]>properties.filter(p => p.hidden == false);

  for (let p of filteredProps) {
    p.cash_on_cash_mortgage = undefined;
    p.total_return_mortgage = undefined;
  }
  let [res, err] = await API.recalc({
    ...params,
    prop_details: filteredProps.map((p: SearchResult) => ({
      prop_id: p.prop_id,
      price: p.price,
      market_rent: p.predicted_rent
    }))
  });

  if (err)
    return console.error(err);

  let propsKeys:Record<string, TSearchRequest__RecalcMortageRow> = {};
  for (let p of res.data.result)
    propsKeys[p.prop_id] = p;
  
  for (let p of filteredProps) {
    let pid = (<SearchResult>p).prop_id;
    if (propsKeys[pid]) {
      p.cash_on_cash_mortgage = propsKeys[pid].cash_on_cash;
      p.total_return_mortgage = propsKeys[pid].total_return;
    }
  }
}

export function toObject(url: string) {
  return qs.parse(url, { parseBooleans: true, parseNumbers: true });
}

export function toUrl(object: object) {
  return qs.stringify(object);
}

export async function autoCompleteQuery(query: string) {
  let [res, err] = await API.elasticQuery({ query });
  if (err)
    return [];
  return res.data.items;
}

export async function getRectQuery(query: string) {
  let [res, err] = await API.rectQuery({ query });

  if (err)
    return false;
  return res.data;
}

export default {
  searchResults,
  toObject,
  toUrl,
  findProperties,
  recalculateByMortgage,
  autoCompleteQuery,
  getRectQuery
}*/