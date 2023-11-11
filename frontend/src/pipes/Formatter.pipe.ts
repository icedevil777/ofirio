import IntlPipe from '@/pipes/Intl.pipe';
import ENUMS from '@/constants/Enums';

export default {
  number(value:any) {
    return IntlPipe['number'].format(value);
  },
  miles(value:any) {
    return IntlPipe['number'].format(value) + ' mi';
  },
  number2Digits(value:any) {
    return IntlPipe['number2Digits'].format(value);
  },
  usd(value:any) {
    return IntlPipe['usd'].format(value);
  },
  usdInt(value:any) {
    return IntlPipe['usd_onlyInt'].format(value);
  },
  usdIntSigned(value:any) {
    return IntlPipe['usd_onlyIntSigned'].format(value);
  },
  '%'(value:any) {
    return IntlPipe['percent'].format(value);
  },
  '%Int'(value:any) {
    return IntlPipe['percentInt'].format(value);
  },
  '%Signed'(value:any) {
    return IntlPipe['percentSigned'].format(value);
  },
  'date'(value:any) {
    try {
      if (!(value instanceof Date))
        value = new Date(value);
      
      return IntlPipe['date'].format(value);
    } catch (ex) {
      return 'n/a';
    }
  },
  'dateTime'(value:any) {
    try {
      if (!(value instanceof Date))
        value = new Date(value);

      return IntlPipe['dateTime'].format(value);
    } catch (ex) {
      return 'n/a'
    }
  },
  enum(name:string, value: any) {
    if (ENUMS[name] == undefined)
      return undefined;
    
    return ENUMS[name][value];
  },
  enumSafe(name:string, value: any) {
    if (ENUMS[name] == undefined)
      return value;

    const val = ENUMS[name][value];
    if (val == undefined)
      return value;

    return val;
  }
}