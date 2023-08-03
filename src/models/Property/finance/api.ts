import axios from 'axios';
import { of } from 'await-of';
import { TPropertyDTO_Financial } from '@/models/Property/finance';

export type TPropertyDTO__Client_Calculator = {
  prop_id: string,
  price?: number,
  monthly_rent?: number,
  down_payment?:number,
  financing_years?:number,
  interest_rate?:number,
  hoa_fees?: number,
  insurance?: number,
  property_taxes?: number,
  annual_increase_rent?: number,
  annual_increase_prop?: number,
  general_inflation?: number,
  average_length_stay_years?: number,
  management_fees_percent?: number,
  maintenance_cost_percent?: number,
  overhead_cost_percent?: number,
  closing_cost_on_purchase_percent?: number,
  closing_cost_on_sale_percent?: number,
  vacancy_per_year_days?: number,
  release_fees_amount?: number,
  overhead_cost_amount?: number,
  maintenance_cost_amount?: number
}

export default {
  calculate: function (data:TPropertyDTO__Client_Calculator) {
    return <AxiosRequestToAwaiting<TPropertyDTO_Financial>>of(axios.post(`/api/property/finance`, data));
  }
}