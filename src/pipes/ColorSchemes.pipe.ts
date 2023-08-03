export const colorSchemePipe:Record<string, Function> = {
  'red': function () { return '#ef4b44'; },
  'orange': function () { return '#ff9900'; },
  'green': function () { return '#01d092'; },
  'blue': function () { return '#57c0ff'; },

  'cap-coc': function (value:number) {
    if (value < 0) return colorSchemePipe.red();
    else if (value <= 0.02) return '';
    else if (value <= 0.05) return colorSchemePipe.orange();
    else return colorSchemePipe.green();
  },
  'perf': function (value:number) {
    if (value < 0) return colorSchemePipe.red();
    else if (value <= 0.02) return '';
    else if (value <= 0.05) return colorSchemePipe.orange();
    else return colorSchemePipe.green();
  },
  'tenPointRating': function (value:number) {
    if (value < 3) return colorSchemePipe.red();
    else if (value >= 8) return colorSchemePipe.green();
    else return '';
  },
  'posNeg': function (value:number) {
    if (value < 0) return colorSchemePipe.red();
    else if (value > 0) return colorSchemePipe.green();
    else return '';
  },
  'invPosNeg': function (value:number) {
    if (value > 0) return colorSchemePipe.red();
    else if (value < 0) return colorSchemePipe.green();
    else return '';
  },
  'rentAnalyzerMarker': function (value:string) {
    if (value == 'higher')
      return colorSchemePipe.red();
    else if (value == 'moderate')
      return colorSchemePipe.blue();
    else if (value == 'lower')
      return colorSchemePipe.green();
  },
}

export function colorSchemePipeStyle(scheme: string, value: any) {
  if (colorSchemePipe[scheme] && value != undefined && value != null)
    return { color: colorSchemePipe[scheme](value) };
  return {};
}