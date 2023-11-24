import { AccountStoreType } from '@/models/Account';
import VueStore from 'vue-class-store';
import envModel from '@/models/env.model';
import authApi from './api';
import { observe } from '@/services/LocalstorageWatcher.service';
import CSRFTokenService from '@/services/CSRFToken.service';
import router from '@/router';

import { APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED } from '@/constants/DefaultMessages';

export type TAccountDTO__SocialUrls = Record<string, string>

let Account: AccountStoreType;

@VueStore
export default class AccountAuthModule {

  private _isLoggedIn = false;
  private _socialLoginUrls: TAccountDTO__SocialUrls | null = null;

  private _inited = false;
  private _initialPromise!: Promise<void>;
  private _initialPromiseResolver!: Function;

  constructor(AccountRef: AccountStoreType) {
    Account = AccountRef;

    this._initialPromise = new Promise((res) => {
      this._initialPromiseResolver = res;
    });

    observe('ofirio-action-reload-auth', () => {
      this.loadAccountDTO();
    })
  }

  public async getSocialLoginUrls() {
    const [res, err] = await authApi.getSocialUrls();
    if (err)
      return console.warn('Account:Auth:getSocialLoginUrls :: server error');

    this._socialLoginUrls = res.data;
    for (let key in this._socialLoginUrls)
      if (envModel.VUE_APP_API_URL_PREFIX)
        this._socialLoginUrls[key] = envModel.VUE_APP_API_URL_PREFIX.substr(0, envModel.VUE_APP_API_URL_PREFIX.length - 1) + this._socialLoginUrls[key];
  }

  public get inited() {
    return this._inited;
  }
  
  public get initPromise() {
    return this._initialPromise;
  }
  public get isLoggedIn() {
    return this._isLoggedIn;
  }
  public get socialLoginUrls() {
    return this._socialLoginUrls;
  }

  public async loadAccountDTO() {
    const [res, err] = await authApi.getAccount();

    setTimeout(() => {
      try {
        this._inited = true;
        this._initialPromiseResolver();
      } catch (ex) {}
    }, 0);

    if (err) {
      if (err.response?.status != 401)
        console.error('Account:Auth :: Invalid response code');
        
      this._isLoggedIn = false;
      Account.Basis.setDTO(null);
      Account.Profile.setDTO(null);
      Account.Subscriptions.load().catch(() => {});
      return false;
    }

    Account.Basis.setDTO(res.data);
    Account.Profile.setDTO(res.data);
    Account.Subscriptions.load().catch(() => {});
    return this._isLoggedIn = true;
  }

  async login(email: string, password: string) {
    const [res, err] = await authApi.login({ email, password });
    console.log('login res', res)
    if (err) {
      if (err.response?.status != 400) {
        console.error('Account:Auth :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
      }
      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return false;
    }
    
    await CSRFTokenService.refreshCSRFToken();
    this.loadAccountDTO();
    return true;
  }

  async logout() {
    const [res, err] = await authApi.logout();

    if (err) {
      if (err.response?.status != 400) {
        console.error('Account:Auth :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
      }
      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return false;
    }

    await CSRFTokenService.refreshCSRFToken();
    const loggedIn = await this.loadAccountDTO();
    if (!loggedIn)
      router.push('/');
    return true;
  }

  async changePassword(oldPassword: string, newPassword: string) {
    const [res, err] = await authApi.updatePassword({
      password_new: newPassword,
      password_old: oldPassword
    });

    if (err) {
      if (err.response?.status != 400) {
        console.error('Account:Auth :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
      }
      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return false;
    }
    return true;
  }

  async startPasswordReset(email: string) {
    const [res, err] = await authApi.initiatePasswordRestore({ email });

    if (err) {
      console.error('Account:Auth :: Invalid response code');
      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return false;
    }
    
    return true;
  }


  async checkPasswordResetToken(token: string) {
    const [res, err] = await authApi.checkPasswordRestoreToken({
      restore_code: token
    });

    if (err) {
      if (err.response?.status != 400) {
        console.error('Account:Auth :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
      }
      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return false;
    }
    return true;
  }


  async changePasswordByResetToken(token: string, newPassword: string) {
    const [res, err] = await authApi.completeRestorePassword({
      restore_code: token,
      password_new: newPassword
    });

    if (err) {
      if (err.response?.status != 400) {
        console.error('Account:Auth :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
      }
      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return false;
    }
    return true;
  }


  async register(email: string, password: string) {
    const [res, err] = await authApi.registerAccount({ email, password });

    if (err) {
      if (err.response?.status != 400) {
        console.error('AccountDTO :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
      }
      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return false;
    }

    await CSRFTokenService.refreshCSRFToken();
    this.loadAccountDTO();
    return true;
  }

}