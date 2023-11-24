import axios from 'axios';
import { of } from 'await-of';
import { TRentEstimate_Query } from '../RentEstimator/api';
import { TPropertyDTO__Client_Calculator } from '../Property/finance/api';

export type TReportDTO__ListItem = {
  created_at: string,
  report_type: 'rent_analyzer' | 'property',
  query: Record<string, any>,
  report_file: string
}

export type TReportDTO__ReportLink = {
  report_file: string
}


let getUrl = ''
if (location.hostname === 'localhost') {
  getUrl = 'https://localhost'
}

export default {

  loadReportsList: function () {
    return <AxiosRequestToAwaiting<TReportDTO__ListItem[]>>of(axios.get(`${getUrl}/api/report/reports`));
  },

  reportRentAnal: function (data: TRentEstimate_Query) {
    return <AxiosRequestToAwaiting<TReportDTO__ReportLink>>of(axios.post(`${getUrl}/api/report/rent_analyzer`, data));
  },

  reportProperty: function (data: TPropertyDTO__Client_Calculator) {
    return <AxiosRequestToAwaiting<TReportDTO__ReportLink>>of(axios.post(`${getUrl}/api/report/property`, data));
  }
}