import API from './api';
import VueStore from 'vue-class-store';
import { of } from 'await-of';
import { PropertyStoreType } from '@/models/Property';

export type TPropertyDTO_Financial_CustomParams = {
  price?: number, 
  monthly_rent?: number, 
  down_payment?: number, 
  financing_years?: number, 
  interest_rate?: number, 
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
  [key: string]: undefined | number
};

export type TPropertyDTO_Financial = {
  base: {
    price: number,
    monthly_rent: number,
    down_payment: number,
    financing_years: number,
    interest_rate: number
  },
  main_results: {
    rental_income: number,
    expenses: number,
    cash_flow: number,
    cash_on_cash: number,
    cap_rate: number,
    total_return: number
  },
  detailed: {
    annual_increase_rent: number,
    annual_increase_prop: number,
    general_inflation: number,
    average_length_stay_years: number,
    management_fees_percent: number,
    maintenance_cost_percent: number,
    overhead_cost_percent: number,
    closing_cost_on_purchase_percent: number,
    closing_cost_on_sale_percent: number,
    vacancy_per_year_days: number,
    release_fees_amount: number,
    overhead_cost_amount: number,
    maintenance_cost_amount: number,
  },
  monthly_cash_flow: {
    month_rent_less_vacancy: number,
    month_management_fees: number,
    month_maintenance_reserves: number,
    month_hoa_fees: number,
    month_insurance: number,
    month_property_taxes: number,
    month_re_lease_fees: number,
    month_overhead_miscellanous: number,
    month_operating_income: number,
    month_loan_payments: number,
    net_income: number,
    month_cash_income_loss: number
  },
  performance: {
    equity_investment: number,
    loan_value: number,
    total_investment: number,
    cash_flow_year1: number,
    operating_income_year1: number,
    net_income_year1: number,
    cap_rate_year1: number,
    cash_on_cash_year1: number,
    one_percent_rule: number,
    gross_yield: number,
    irr: number,
    operating_expense_ratio_year1: number,
    debt_service_coverage_year1: number
  },
  proforma: {
    year: Record<string, number>,
    rent: Record<string, number>,
    vacancy_costs_empty: Record<string, number>,
    rent_less_vacancy: Record<string, number>,
    management_fees: Record<string, number>,
    maintenance_reserves: Record<string, number>,
    hoa_fees: Record<string, number>,
    insurance: Record<string, number>,
    property_taxes: Record<string, number>,
    re_lease_fees: Record<string, number>,
    overhead_miscellanous: Record<string, number>,
    operating_expenses: Record<string, number>,
    operating_income: Record<string, number>,
    operating_income_margin: Record<string, number>,
    interest_payments: Record<string, number>,
    net_income: Record<string, number>,
    net_income_margin: Record<string, number>,
    loan_payments: Record<string, number>,
    cash_flow: Record<string, number>
  },
  accumulated_wealth: {
    year: Record<string, number>,
    cash_flow_from_operations: Record<string, number>,
    projected_accummulated_wealth: Record<string, number>,
    property_appreciation: Record<string, number>,
    eqity: Record<string, number>,
    loan_balance: Record<string, number>
  }
}
let Property: PropertyStoreType;

@VueStore
export default class PropertyFinanceModule {

  private id!: string;
  private _dto: TPropertyDTO_Financial | null = null;
  private _dtoDefault: TPropertyDTO_Financial | null = null;
  private _customizationParams: TPropertyDTO_Financial_CustomParams | null = null;
  
  private _ready: boolean = false;
  private _readyPromise!: Promise<void>;
  private _readyPromiseResolve!: Function;
  private _readyPromiseReject!: Function;

  constructor () {
    this._readyPromise = new Promise((res, rej) => {
      this._readyPromiseReject = rej;
      this._readyPromiseResolve = res;
    });
  }

  public async init(id: string, propObject: PropertyStoreType, financialData?: object) {
    this.id = id;
    Property = propObject;
    const [res, err] = await of(this.load(financialData || {}));
    
    this._dtoDefault = JSON.parse(JSON.stringify(this._dto));
    this._customizationParams = {
      price: this._dtoDefault?.base.price,
      monthly_rent: this._dtoDefault?.base.monthly_rent,
      down_payment: this._dtoDefault?.base.down_payment,
      financing_years: this._dtoDefault?.base.financing_years,
      interest_rate: this._dtoDefault?.base.interest_rate,
      hoa_fees: this._dtoDefault?.monthly_cash_flow.month_hoa_fees,
      insurance: this._dtoDefault?.monthly_cash_flow.month_insurance,
      property_taxes: this._dtoDefault?.monthly_cash_flow.month_property_taxes,
      annual_increase_rent: this._dtoDefault?.detailed.annual_increase_rent,
      annual_increase_prop: this._dtoDefault?.detailed.annual_increase_prop,
      general_inflation: this._dtoDefault?.detailed.general_inflation,
      average_length_stay_years: this._dtoDefault?.detailed.average_length_stay_years,
      management_fees_percent: this._dtoDefault?.detailed.management_fees_percent,
      maintenance_cost_percent: this._dtoDefault?.detailed.maintenance_cost_percent,
      overhead_cost_percent: this._dtoDefault?.detailed.overhead_cost_percent,
      closing_cost_on_purchase_percent: this._dtoDefault?.detailed.closing_cost_on_purchase_percent,
      closing_cost_on_sale_percent: this._dtoDefault?.detailed.closing_cost_on_sale_percent,
      vacancy_per_year_days: this._dtoDefault?.detailed.vacancy_per_year_days,
      release_fees_amount: this._dtoDefault?.detailed.release_fees_amount,
      overhead_cost_amount: this._dtoDefault?.detailed.overhead_cost_amount,
      maintenance_cost_amount: this._dtoDefault?.detailed.maintenance_cost_amount
    }

    if (res) {
      setTimeout(() => {
        this._ready = true;
        this._readyPromiseResolve();
      }, 0);
    } else if (res === false || err) {
      setTimeout(() => {
        this._ready = false;
        this._readyPromiseReject();
      }, 0);
    }
  }

  public async load(options?: object) {
    const [res, err] = await API.calculate({ prop_id: this.id, ...options });

    if (err) {
      if (![200, 400, 404].includes(<number>err.response?.status))
        console.error('Property:Financial :: Invalid response code');
      this._dto = <any>{
        base: {
          price: Property.Basis.dto?.data.price,
          monthly_rent: Property.Basis.dto?.data.predicted_rent,
          down_payment: 0.6,
          financing_years: 15,
          interest_rate: 0.30
        },
        main_results: {},
        detailed: {},
        monthly_cash_flow: {},
        performance: {},
        proforma: {},
        accumulated_wealth: {}
      };
      return false;
    }

    this._dto = res.data;
    return true;
  }

  public get dto() {
    return this._dto;
  }

  public get defaultDto() {
    return JSON.parse(JSON.stringify(this._dtoDefault));
  }

  public getCustomizationParams() {
    return JSON.parse(JSON.stringify(this._customizationParams));
  }

  public get isReady() {
    return this._ready;
  }

  public get isReadyPromise() {
    return this._readyPromise;
  }

}