import qs from 'query-string';
import { Ref, ref } from 'vue';
import AccountStore from '@/models/Account';
import API, { TSearchRequest, TSearchRequest__Filters, TSearchRequest__RecalcMortage, TSearchRequest__RecalcMortageRow, TSearchRequest__Sort } from './api';

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
  map?: Record<string, Array<HiddenSearchResult|SearchResult>>,
  geo_shape?: {
    boundary: any,
    center: {
      latitude: number,
      longitude: number
    }
  }
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
    map: {},
    geo_shape: undefined
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
  
  const geo_rectReal = type == 'geo' && typeof parsedSearchType.geo_rect == 'string' && parsedSearchType.geo_rect.includes(',');
  
  if (additionalOpts?.map) {
    bounds = additionalOpts.map.getBounds();
    bounds = bounds ? bounds.toUrlValue() : undefined;
    if (bounds && (type != 'geo' || !additionalOpts.noMapParams))
      zoomLevel = additionalOpts.map.getZoom();
    
    bounds = type == 'geo' && additionalOpts.searchRegions.length == 0 && geo_rectReal ? parsedSearchType.geo_rect : bounds;
  }

  map_query = true;

  //@ts-ignore
  const query:TSearchRequest = {
    type,
    ...parsedSearchType,
    ...parsedSearchOptions,
    ...parsedSearchSorting,
    start: offset,
    map_query,
    //@ts-ignore
    viewport: bounds,
    zoom: zoomLevel,
    map_height: additionalOpts?.cssBoundary?.height,
    map_width: additionalOpts?.cssBoundary?.width
  }

  if (type == 'geo') {
    if (additionalOpts.searchRegions.length > 0 && !geo_rectReal) {
      //@ts-ignore
      query.geo_polygons = additionalOpts.searchRegions.map((r:any) => {
        const paths = r.paths.getArray().map((c:any) => {
          return [c.lng(), c.lat()];
        })

        if (paths[0].join(';') != paths[paths.length - 1].join(';'))
          paths.push(paths[0]);

        return paths;
      });
      //@ts-ignore
      query.geo_rect = undefined;
    }
  } else if (additionalOpts.noMapParams) {
    query.viewport = undefined;
    query.zoom = undefined;
  }

  let [res, err] = await API.search(query);
  if (!err)
    if (res.data) {
      if (searchResults.value == null)
        searchResults.value = defNUllResponse;

      if (searchResults.value != null) {
        searchResults.value.geo_shape = res.data.geo_shape;
        searchResults.value.mode = res.data.mode;
        searchResults.value.hidden_in_total = res.data.hidden_in_total;
        searchResults.value.search = res.data.search;
        searchResults.value.map = res.data.map;
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
}