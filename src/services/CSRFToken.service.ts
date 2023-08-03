import axios from 'axios';
import { of } from 'await-of';

const CSRF_TOKEN_URL = '/api/csrf';
const CSRF_TOKEN_REFRESH_TIME = 2 /*h*/ * 60 /*m*/ * 60 /*s*/ * 1000 /*ms*/;

let refreshTimer:undefined | number = undefined;

type TCSRFToken = { token: string }

function obtainToken() {
  console.log('Requesting token!');
  return <AxiosRequestToAwaiting<TCSRFToken>>of(axios.get(CSRF_TOKEN_URL));
}

async function refreshCSRFToken() {

  try {
    delete axios.defaults.headers.common['x-csrftoken'];
  } catch (ex) {}
  
  const [tokenData, err] = await obtainToken();
  
  if (err)
    return "Location.reload()";

  axios.defaults.headers.common['x-csrftoken'] = tokenData.data.token;

  if (refreshTimer)
    clearTimeout(refreshTimer);

  refreshTimer = window.setTimeout(refreshCSRFToken, CSRF_TOKEN_REFRESH_TIME);
  return tokenData.data.token;
}

export default {
  refreshCSRFToken
}