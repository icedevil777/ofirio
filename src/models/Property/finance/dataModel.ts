import * as yup from 'yup';
import { TPropertyDTO_Basis } from '@/models/Property/basis';
import AccountStore from '@/models/Account';

export type TDataModel = {
  min?: number,
  max?: number,
  type: string,
  debounce?: number,
  validator: yup.AnySchema
}

yup.addMethod(yup.number, 'isMultipleOf', function (number, errorMessage) {
  return this.test(`number-is-multiple-of`, errorMessage, function (value: any) {
    const { path, createError } = this;

    return (
      value % number === 0 ||
      createError({ path, message: errorMessage })
    );
  });
});

const model:Record<string, any> = {
  purchase_price: function(price:number) {
    const min = Math.floor((price != undefined ? Math.round(0.5 * price / 1000) * 1000 : 0) / 10) * 10;
    const max = Math.ceil((price != undefined ? Math.round(1.5 * price / 1000) * 1000 : 1000) / 10) * 10;
    return {
      min,
      max,
      step: 100,
      type: 'number',
      prefix: '$',
      get validator() {
        return yup.number().required('Value is required')
          .typeError('You must specify a number')
          .min(min, `Minimum value is ${min}`)
          .max(max, `Maximum value is ${max}`);
      }
    }
  },
  slider__purchase_price: {
    stops: [0.5],
    tooltips: false,
    disabled: AccountStore.Basis.isPremium ? undefined : true
  },
  down_payment: function(dto: TPropertyDTO_Basis) {
    return {
      min: 20,
      max: 100,
      step: 5,
      type: 'number',
      postfix: '%',
      disabled: AccountStore.Basis.isPremium && !dto?.is_cash_only ? undefined : true,
      get validator() {
        return yup.number().required('Value is required')
          .typeError('You must specify a number')
          .min(model.down_payment().min, 'Minimum value is 20')
          .max(model.down_payment().max, 'Maximum value is 100')
          //@ts-ignore
          .isMultipleOf(model.down_payment().step, 'Use values with step 5%');
      }
    }
  },
  slider__down_payment: {
    min: 0.2,
    max: 1,
    step: 0.05,
    stops: [0],
    stopBuffer: 0.05,
    tooltips: false
  },
  estimated_rent: function(dto: TPropertyDTO_Basis) {
    const min = Math.floor((dto?.data.min_range_rent != undefined ? dto.data.min_range_rent : 1000) / 10) * 10;
    const max = Math.ceil((dto?.data.max_range_rent != undefined ? dto.data.max_range_rent : 10000) / 10) * 10;

    return {
      min,
      max,
      step: 10,
      type: 'number',
      prefix: '$',
      get validator() {
        return yup.number().required('Value is required')
          .typeError('You must specify a number')
          .min(min, `Minimum value is ${min}`)
          .max(max, `Maximum value is ${max}`);
      }
    }
  },
  slider__estimated_rent: function (dto: TPropertyDTO_Basis) {
    const min = dto?.data.min_range_rent != undefined ? dto.data.min_range_rent : 1000;
    const max = dto?.data.max_range_rent != undefined ? dto.data.max_range_rent : 10000;
    const predRent = dto?.data.predicted_rent != undefined ? dto.data.predicted_rent : 6000;
    const range = max - min;

    return {
      stops: [ (predRent - min) / range ],
      stopBuffer: 20,
      tooltips: false,
      disabled: AccountStore.Basis.isPremium ? undefined : true
    }
  },
  financing_years: function(dto: TPropertyDTO_Basis) {
    return {
      min: 5,
      max: 30,
      step: 5,
      type: 'number',
      postfix: 'years',
      disabled: dto?.is_cash_only ? true : undefined,
      get validator() {
        return yup.number().required('Value is required')
          .typeError('You must specify a number')
          .min(model.financing_years().min, 'Minimum value is 5')
          .max(model.financing_years().max, 'Maximum value is 30');
      }
    }
  },
  slider__financing_years: {
    tooltips: false
  },
  interest_rate: function(dto: TPropertyDTO_Basis) {
    return {
      min: 1.5,
      max: 20,
      step: 0.01,
      type: 'number',
      postfix: '%',
      disabled: dto?.is_cash_only ? true : undefined,
      get validator() {
        return yup.number().required('Value is required')
          .typeError('You must specify a number')
          .min(model.interest_rate().min, 'Minimum value is 1.5')
          .max(model.interest_rate().max, 'Maximum value is 20');
      }
    }
  },
  slider__interest_rate: {
    min: 0.015,
    max: 0.20,
    step: 0.0001,
    tooltips: false
  },
  property_taxes: {
    min: 1,
    step: 1,
    type: 'number',
    prefix: '$',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.property_taxes.min, 'Minimum value is 1')
    }
  },
  insurance: {
    min: 1,
    step: 1,
    type: 'number',
    prefix: '$',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.insurance.min, 'Minimum value is 1')
    }
  },
  homeowner_assoc: {
    min: 0,
    step: 1,
    type: 'number',
    prefix: '$',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.homeowner_assoc.min, 'Minimum value is 0')
    }
  },
  management_fees: {
    min: 0,
    max: 100,
    step: 1,
    type: 'number',
    postfix: '%',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.management_fees.min, 'Minimum value is 0')
        .max(model.management_fees.max, 'Maximum value is 100');
    }
  },
  maintenance_reserves: {
    min: 0,
    max: 100000,
    step: 1,
    type: 'number',
    prefix: '$',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.agent_leasing_fees.min, `Minimum value is ${model.agent_leasing_fees.min}`)
        .max(model.agent_leasing_fees.max, `Maximum value is ${model.agent_leasing_fees.max}`);
    }
  },
  annual_increase_in_prop_value: {
    min: 0,
    max: 100,
    step: 1,
    type: 'number',
    postfix: '%',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.annual_increase_in_prop_value.min, 'Minimum value is 0')
        .max(model.annual_increase_in_prop_value.max, 'Maximum value is 100');
    }
  },
  average_length_of_tenant_stay: {
    min: 1,
    step: 1,
    type: 'number',
    postfix: 'years',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.average_length_of_tenant_stay.min, 'Minimum value is 1')
    }
  },
  vacancy: {
    min: 0,
    max: 364,
    step: 1,
    type: 'number',
    postfix: 'days',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.vacancy.min, `Minimum value is ${model.vacancy.min}`)
        .max(model.vacancy.max, `Maximum value is ${model.vacancy.max}`)
    }
  },
  annual_increase_in_rent: {
    min: 0,
    max: 100,
    step: 1,
    type: 'number',
    postfix: '%',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.annual_increase_in_rent.min, 'Minimum value is 0')
        .max(model.annual_increase_in_rent.max, 'Maximum value is 100');
    }
  },
  general_inflation: {
    min: 0,
    max: 100,
    step: 1,
    type: 'number',
    postfix: '%',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.general_inflation.min, 'Minimum value is 0')
        .max(model.general_inflation.max, 'Maximum value is 100');
    }
  },
  closing_costs_on_purchase: {
    min: 0,
    max: 100,
    step: 1,
    type: 'number',
    postfix: '%',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.closing_costs_on_purchase.min, 'Minimum value is 1')
        .max(model.closing_costs_on_purchase.max, 'Maximum value is 100');
    }
  },
  closing_costs_on_sale: {
    min: 0,
    max: 100,
    step: 1,
    type: 'number',
    postfix: '%',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.closing_costs_on_sale.min, 'Minimum value is 0')
        .max(model.closing_costs_on_sale.max, 'Maximum value is 100');
    }
  },
  agent_leasing_fees: {
    min: 0,
    max: 100000,
    step: 1,
    type: 'number',
    prefix: '$',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.agent_leasing_fees.min, `Minimum value is ${model.agent_leasing_fees.min}`)
        .max(model.agent_leasing_fees.max, `Maximum value is ${model.agent_leasing_fees.max}`);
    }
  },
  overhead_miscellanous: {
    min: 0,
    max: 100000,
    step: 1,
    type: 'number',
    prefix: '$',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.agent_leasing_fees.min, `Minimum value is ${model.agent_leasing_fees.min}`)
        .max(model.agent_leasing_fees.max, `Maximum value is ${model.agent_leasing_fees.max}`);
    }
  },
  cap_rate: {
    min: 0,
    max: 20,
    step: 1,
    type: 'number',
    postfix: '%',
    prepend: 'Min',
    disabled: AccountStore.Basis.isPremium ? undefined : true,
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.cap_rate.min, `Minimum value is ${model.cap_rate.min}`)
        .max(model.cap_rate.max, `Maximum value is ${model.cap_rate.max}`);
    }
  },
  slider__cap_rate: {
    min: 0,
    max: 0.2,
    step: 0.01,
    tooltips: false,
    disabled: AccountStore.Basis.isPremium ? undefined : true
  },
  coc_return: {
    min: 0,
    max: 100,
    step: 1,
    type: 'number',
    postfix: '%',
    prepend: 'Min',
    disabled: AccountStore.Basis.isPremium ? undefined : true,
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.coc_return.min, `Minimum value is ${model.coc_return.min}`)
        .max(model.coc_return.max, `Maximum value is ${model.coc_return.max}`);
    }
  },
  slider__coc_return: {
    min: 0,
    max: 1,
    step: 0.01,
    tooltips: false,
    disabled: AccountStore.Basis.isPremium ? undefined : true
  },
  cash_flow: {
    min: 0,
    max: 25000,
    step: 100,
    type: 'number',
    prefix: '$',
    prepend: 'Min',
    disabled: AccountStore.Basis.isPremium ? undefined : true,
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.cash_flow.min, 'Minimum value is 0')
        .max(model.cash_flow.max, 'Maximum value is 25000');
    }
  },
  slider__cash_flow: {
    tooltips: false
  },
  beds: {
    min: 0,
    max: 9999,
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.beds.min, 'Minimum value is 0')
        .max(model.beds.max, 'Maximum value is 9999');
    }
  },
  baths: {
    min: 0,
    max: 9999,
    postfix: '+',
    get validator() {
      return yup.number().required('Value is required')
        .typeError('You must specify a number')
        .min(model.baths.min, 'Minimum value is 0')
        .max(model.baths.max, 'Maximum value is 9999');
    }
  }
}

export default model;