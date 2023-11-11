import API, { TRentEstimate_Query, TRentEstimate_Result } from './api';
import ReportAPI, { TReportDTO__ReportLink } from '@/models/Reports/api';
// import Chicken from '@/models/Henhouse/Chicken.model';
// import { Egg, EggEnum } from '@/models/Henhouse/Egg.model';

export default {
  query: async function (params: TRentEstimate_Query):Promise<[ null|TRentEstimate_Result, null|string ]> {
    let [res, err] = await API.query(params);
    
    if (err) {
      const code = err.response?.status;
      if (code === 401)
        return [ null, 'You are not authorized' ];

      else if (code === 400)
        return [ null, 'Address not found' ];

      else if (code === 403)
        return [ null, 'Limits reached' ];

      else if (code === 404)
        return [ null, 'No properties found' ];

      else if (code === 500)
        return [ null, 'Server error' ];

      return [ null, null ];
    }
    res.data.items.forEach(e => {
      const coords = e.location.substr(1, e.location.length - 2);
      [e.lat, e.lon] = coords.split(',').map(c => parseFloat(c));
    });
    
    return [ res.data, null ];
  },

  generateReport: async function (params: TRentEstimate_Query):Promise<[ null|TReportDTO__ReportLink, null|string ]> {

    let [res, err] = await ReportAPI.reportRentAnal(params);
    
    if (err) {
      const code = err.response?.status;
      if (code === 401)
        return [ null, 'You are not authorized' ];

      return [ null, null ];
    }
    
    return [ res.data, null ];
  }
}

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
/*
export function RentEstimatorModelMixin(pure: boolean = false) {

  const HenHouse = {
    model: Chicken({
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
        validators: []
      })
    }),
    actions: {
      query: async function ():Promise<[ null|TRentEstimate_Result, null|string ]> {
        const snap = HenHouse.model.$snapshot();

        let [res, err] = await API.query({
          baths: snap.baths,
          beds: snap.beds,
          distance: snap.distance,
          look_back: snap.look_back,
          prop_type2: snap.prop_type2,
          type: snap.searchMode,
          query: snap.query,
          prop_id: snap.prop_id ? snap.prop_id : undefined,
          building_size: snap.searchMode == 'address' ? (snap.building_size || undefined) : undefined,
        });
        
        if (err) {
          const code = err.response?.status;
          if (code === 401)
            return [ null, 'You are not authorized' ];
    
          else if (code === 400)
            return [ null, 'Address not found' ];
    
          else if (code === 403)
            return [ null, 'Limits reached' ];
    
          else if (code === 404)
            return [ null, 'No properties found' ];
    
          else if (code === 500)
            return [ null, 'Server error' ];
    
          return [ null, null ];
        }
        res.data.items.forEach(e => {
          const coords = e.location.substr(1, e.location.length - 2);
          [e.lat, e.lon] = coords.split(',').map(c => parseFloat(c));
        });
        
        return [ res.data, null ];
      },
    
      generateReport: async function ():Promise<[ null|TReportDTO__ReportLink, null|string ]> {
        const snap = HenHouse.model.$snapshot();

        let [res, err] = await ReportAPI.reportRentAnal({
          baths: snap.baths,
          beds: snap.beds,
          distance: snap.distance,
          look_back: snap.look_back,
          prop_type2: snap.prop_type2,
          type: snap.searchMode,
          query: snap.query,
          prop_id: snap.prop_id ? snap.prop_id : undefined,
          building_size: snap.searchMode == 'address' ? (snap.building_size || undefined) : undefined,
        });
        
        if (err) {
          const code = err.response?.status;
          if (code === 401)
            return [ null, 'You are not authorized' ];
    
          return [ null, null ];
        }
        
        return [ res.data, null ];
      }
    }
  }

  return pure ? HenHouse : {
    data() {
      return {
        RentEstimatorModel: HenHouse
      }
    }
  }
}*/