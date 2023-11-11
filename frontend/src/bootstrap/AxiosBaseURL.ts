import axios from 'axios';
import envModel from '@/models/env.model';

export default async function () {
  if (process.env.NODE_ENV == 'development') {
    axios.defaults.baseURL = envModel.VUE_APP_API_URL_PREFIX;
    axios.defaults.withCredentials = true;
  }
}