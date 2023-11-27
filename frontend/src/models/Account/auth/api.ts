import { TAccountBaseDTO } from '@/models/Account/basis';
import axios from 'axios';
import { of } from 'await-of';
import { TAccountDTO__SocialUrls } from '@/models/Account/auth';


type TAccountDTO__Client_Login = {
  email: string,
  password: string
}

type TAccountDTO__Client_Registration = {
  first_name?: string,
  last_name?: string,
  email: string,
  password: string
}

type TAccountDTO__Client_RestorePassword = {
  email: string
}

type TAccountDTO__Client_RestoreTokenCheck = {
  restore_code: string
}

type TAccountDTO__Client_RestorePasswordChange = {
  restore_code: string,
  password_new: string
}

type TAccountDTO__Client_UpdatePassword = {
  password_old: string,
  password_new: string
}

let getUrl = ''
if (location.hostname === 'localhost') {
  getUrl = 'https://localhost'
}

export default {

  getAccount: function () {
    return <AxiosRequestToAwaiting<TAccountBaseDTO>>of(axios.get(`${getUrl}/api/account`));
  },

  login: function (data:TAccountDTO__Client_Login) {
    console.log('login data', data)
    return <AxiosRequestToAwaiting<void>>of(axios.post(`${getUrl}/api/account/session-login`, data));
  },

  logout: function () {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`${getUrl}/api/account/logout`));
  },

  registerAccount: function (data:TAccountDTO__Client_Registration) {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`${getUrl}/api/account/registration`, data));
  },

  initiatePasswordRestore: function (data:TAccountDTO__Client_RestorePassword) {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`${getUrl}/api/account/restore_password`, data));
  },

  checkPasswordRestoreToken: function (data:TAccountDTO__Client_RestoreTokenCheck) {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`${getUrl}/api/account/restore_password_check`, data));
  },

  completeRestorePassword: function (data:TAccountDTO__Client_RestorePasswordChange) {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`${getUrl}/api/account/restore_password_change`, data));
  },

  updatePassword: function (data:TAccountDTO__Client_UpdatePassword) {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`${getUrl}/api/account/change_password`, data));
  },

  getSocialUrls: function () {
    return <AxiosRequestToAwaiting<TAccountDTO__SocialUrls>>of(axios.get(`${getUrl}/api/account/social_urls`));
  }

}