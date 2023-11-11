import axios from 'axios';
import { of } from 'await-of';

export type TRentEstimate_Query = {
  type: 'address' | 'zip' | 'city',
  query: string,
  prop_id?: string,
  distance: 'auto'|'0.1'|'0.2'|'0.33'|'0.50'|'0.75'|'1.0'|'1.5'|'2'|'3'|'5'|'10',
  beds: 'any'|'0'|'1'|'2'|'3'|'4'|'5+',
  baths: 'any'|'1'|'2'|'3'|'4+',
  prop_type2: 'any'|'condo-apt'|'house-duplex',
  look_back: 3|6|9|12|18|24|36|48,
  building_size?: number
}

export type TRentEstimate_ResultTableRow = {
  state_id: string,
  zip: string,
  address: string,
  location: string,
  lat?: number,
  lon?: number,
  beds: number,
  baths: number,
  prop_type2: 'condo-apt',
  building_size: number,
  price_per_ft2: number,
  price: number,
  distance: number,
  type: 'lower'|'moderate'|'higher'
}

export type TRentEstimate_Result = {
  address: {
    state_name: string,
    state_id: string,
    city: string,
    zip_code: string,
    lat: number,
    lon: number,
    formatted_address: string
  },
  rent: {
    average: number,
    median: number,
    prediction: number,
    percentile25: number,
    percentile75: number,
    min: number,
    max: number
  },
  stat: {
    qty: number,
    max_dist: number
  },
  tables: {
    histogram: any,
    rent_by_size: any,
    rent_by_type: any,
    rent_by_beds: any
  },
  items: Array<TRentEstimate_ResultTableRow>
}

export default {

  query: function (data:TRentEstimate_Query) {
    return <AxiosRequestToAwaiting<TRentEstimate_Result>>of(axios.post('/api/rent_estimator', data));
  }

}