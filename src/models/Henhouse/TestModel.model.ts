import { Egg, EggEnum } from '@/models/Henhouse/Egg.model';
import Chicken from '@/models/Henhouse/Chicken.model';

import { VEmail } from '../yups.model';
const DSearchModes = [
  { value: 'address', label: 'Address' },
  { value: 'zip', label: 'Zip' },
  { value: 'city', label: 'City' }
];

const DDistances = [
  { label: 'Auto', value: 'auto' },
  { label: '0.1 miles', value: 0.1 },
  { label: '0.2 miles', value: 0.2 },
  { label: '0.33 miles', value: 0.33 },
  { label: '0.50 miles', value: 0.50 },
  { label: '0.75 miles', value: 0.75 },
  { label: '1 miles', value: 1 },
  { label: '1.5 miles', value: 1.5 },
  { label: '2 miles', value: 2 },
  { label: '3 miles', value: 3 },
  { label: '5 miles', value: 5 },
  { label: '10 miles', value: 10 }
];

const DBeds = [
  { label: 'Any', value: 'any' },
  { label: '0', value: '0' },
  { label: '1', value: '1' },
  { label: '2', value: '2' },
  { label: '3', value: '3' },
  { label: '4', value: '4' },
  { label: '5+', value: '5+' },
];

const DBaths = [
  { label: 'Any', value: 'any' },
  { label: '1', value: '1' },
  { label: '2', value: '2' },
  { label: '3', value: '3' },
  { label: '4+', value: '4+' },
];

const DPropTypes2 = [
  { label: 'Any', value: 'any' },
  { label: 'Condo & Apts.', value: 'condo-apt' },
  { label: 'Single Family', value: 'house-duplex' },
];

const DLookBack = [
  { label: '3 mo', value: 3 },
  { label: '6 mo', value: 6 },
  { label: '9 mo', value: 9 },
  { label: '12 mo', value: 12 },
  { label: '18 mo', value: 18 },
  { label: '24 mo', value: 24 },
  { label: '36 mo', value: 36 },
  { label: '48 mo', value: 48 },
];


export const Model = Chicken({
  searchMode: new EggEnum<string>({
    enum: DSearchModes,
    defaultEnumIndex: 0,
    initialEnumIndex: 0
  }),
  query: new Egg<string>({
    initialValue: ''
  }),
  prop_id: new Egg<string>({
    defaultValue: undefined,
    initialValue: undefined
  }),
  distance: new EggEnum<string | number>({
    enum: DDistances,
    initialEnumIndex: 0,
    defaultEnumIndex: 0
  }),
  beds: new EggEnum<string>({
    enum: DBeds,
    initialEnumIndex: 0,
    defaultEnumIndex: 0
  }),
  baths: new EggEnum<string>({
    enum: DBaths,
    initialEnumIndex: -1,
    defaultEnumIndex: 0
  }),
  prop_type2: new EggEnum<string>({
    enum: DPropTypes2,
    initialEnumIndex: 0,
    defaultEnumIndex: 0
  }),
  look_back: new EggEnum<number>({
    enum: DLookBack,
    initialEnumIndex: 3,
    defaultEnumIndex: 3
  }),
  building_size: new Egg<number>({
    initialValue: undefined,
    defaultValue: undefined,
    validators: [
      VEmail
    ]
  }),


  str: new Egg<string>({
    initialValue: '2',
    defaultValue: '2',
    validators: []
  }),

  bool: new Egg<boolean>({
    initialValue: false,
    defaultValue: false,
    validators: []
  }),

  arr: new Egg<Array<string>>({
    initialValue: [],
    defaultValue: [],
    validators: []
  }),

  inc: new Egg<number>({
    type: 'number',
    min: 0,
    max: 100,
    initialValue: 12,
    validators: [
      yup.number().min(1, 'Minimal password length is 1').max(20, 'Minimal password length is 20')
    ]
  })

})

import * as yup from 'yup';