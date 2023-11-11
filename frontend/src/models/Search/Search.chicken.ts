import Chicken from '@/models/Henhouse/Chicken.model';
import { Egg, EggEnum } from '../Henhouse/Egg.model';

type TProperty_Type2 = 'condo-apt' | 'house-duplex';

export function ChickenDataFactory() {
  return Chicken({

    //TODO: Type this
    priceMode: new EggEnum<'cash' | 'mortgage'>({
      enum: [
        { label: 'Cash', value: 'cash' },
        { label: 'Mortgage', value: 'mortgage' }
      ],
      initialEnumIndex: 0,
      defaultEnumIndex: 0
    }),

    //TODO: Type this
    down_payment: new EggEnum<number>({
      enum: [
        { label: '20%', value: 0.2 },
        { label: '30%', value: 0.3 },
        { label: '40%', value: 0.4 },
        { label: '50%', value: 0.5 }
      ],
      initialEnumIndex: 0,
      defaultEnumIndex: 0
    }),

    //TODO: Type this
    loan_type: new EggEnum<number>({
      enum: [
        { label: '15 years', value: 15 },
        { label: '30 years', value: 30 }
      ],
      initialEnumIndex: 1,
      defaultEnumIndex: 1
    }),

    //TODO: Type this
    interest_rate: new Egg<number>({
      type: 'number',
      initialValue: 0.033,
      defaultValue: 0.033,
    }),


    cap_rate: new Egg<number>({
      type: 'number',
      initialValue: 0,
      defaultValue: 0,
    }),

    coc_rate: new Egg<number>({
      type: 'number',
      initialValue: 0,
      defaultValue: 0,
    }),


    price_min: new Egg<number>({
      type: 'number',
      initialValue: 10000,
      defaultValue: 10000,
      min: 0
    }),

    price_max: new Egg<number>({
      type: 'number',
      initialValue: 1000000,
      defaultValue: 1000000,
    }),


    monthly_rent: new Egg<number>({
      type: 'number',
      initialValue: 1500,
      defaultValue: 1500,
    }),

    prop_type2: new Egg<Array<TProperty_Type2>>({
      initialValue: [],
      defaultValue: []
    }),

    beds_min: new Egg<number>({
      type: 'number',
      min: 0,
      initialValue: 0
    }),

    beds_max: new Egg<number>({
      type: 'number',
      min: 0,
      initialValue: 10
    }),

    baths: new Egg<number>({
      type: 'number',
      min: 0,
      initialValue: 0
    }),



    property_type: new Egg<Array<string>>({
      initialValue: [],
      defaultValue: [],
    }),

    predicted_rent_min: new Egg<number>({
      type: 'number',
      initialValue: 0,
      defaultValue: 0,
    }),

    year_min: new Egg<number>({
      type: 'number',
      min: 1800,
      max: (new Date()).getFullYear(),
      initialValue: 1800
    }),

    year_max: new Egg<number>({
      type: 'number',
      min: 1800,
      max: (new Date()).getFullYear(),
      initialValue: (new Date()).getFullYear()
    }),

    buildingSize_min: new Egg<number>({
      type: 'number',
      min: 0,
      max: 10000,
      initialValue: 0
    }),

    buildingSize_max: new Egg<number>({
      type: 'number',
      min: 0,
      max: 10000,
      initialValue: 10000
    }),

    status_for_sale: new Egg<boolean>({
      initialValue: true,
      defaultValue: true
    }),

    status_pending: new Egg<boolean>({
      initialValue: false,
      defaultValue: false
    }),

    status_sold: new Egg<boolean>({
      initialValue: false,
      defaultValue: false
    }),

    is_55_plus: new Egg<boolean>({
      initialValue: true,
      defaultValue: true
    })

  });
}