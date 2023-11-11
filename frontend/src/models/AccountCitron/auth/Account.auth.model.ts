import envModel from '@/models/env.model';
import authApi from './Account.auth.api';

import { observe } from '@/services/LocalstorageWatcher.service';
import CSRFTokenService from '@/services/CSRFToken.service';
import router from '@/router';

import { APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED } from '@/constants/DefaultMessages';
import { computed } from 'vue';

export type TAccountDTO__SocialUrls = Record<string, string>

export default class AccountAuthModule {

  Account: any;

  private __socialLoginUrls: TAccountDTO__SocialUrls | null = null;
  public socialLoginUrls = computed(() => {
    return this.__socialLoginUrls;
  });

  constructor(AccountRef: any) {

    this.Account = AccountRef;
    // this.getSocialLoginUrls();

    // observe('ofirio-action-reload-auth', () => {
    //   this.loadAccountDTO();
    // })
  }

  public async init() {
    await Promise.allSettled([
      this.load(),
      this.getSocialLoginUrls()
    ]);
  }

  private async getSocialLoginUrls() {
    const [res, err] = await authApi.getSocialUrls();

    if (err)
      return console.warn('Account:Auth:getSocialLoginUrls :: Server Error');

    this.__socialLoginUrls = res.data;
    for (let key in this.__socialLoginUrls)
      if (envModel.VUE_APP_API_URL_PREFIX)
        this.__socialLoginUrls[key] = envModel.VUE_APP_API_URL_PREFIX.substr(0, envModel.VUE_APP_API_URL_PREFIX.length - 1) + this.__socialLoginUrls[key];
  }

  public async load() {
    const [res, err] = await authApi.getAccount();

    if (err) {
      if (err.response?.status != 401)
        console.error('Account:Auth:load :: Invalid response code');

      throw err;
    }

    // Account.Basis.setDTO(res.data);
    // Account.Profile.setDTO(res.data);
    // Account.Subscriptions.load().catch(() => {});
    return this.Account;
  }

  // async login(email: string, password: string) {
  //   const [res, err] = await authApi.login({ email, password });

  //   if (err) {
  //     if (err.response?.status != 400) {
  //       console.error('Account:Auth :: Invalid response code');
  //       throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
  //     }
  //     if (err.response?.data) {
  //       let messages = <TServerDefaultResponse>err.response.data;
  //       throw messages;
  //     }
  //     return false;
  //   }
    
  //   await CSRFTokenService.refreshCSRFToken();
  //   this.loadAccountDTO();
  //   return true;
  // }

  // async logout() {
  //   const [res, err] = await authApi.logout();

  //   if (err) {
  //     if (err.response?.status != 400) {
  //       console.error('Account:Auth :: Invalid response code');
  //       throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
  //     }
  //     if (err.response?.data) {
  //       let messages = <TServerDefaultResponse>err.response.data;
  //       throw messages;
  //     }
  //     return false;
  //   }

  //   await CSRFTokenService.refreshCSRFToken();
  //   const loggedIn = await this.loadAccountDTO();
  //   if (!loggedIn)
  //     router.push('/');
  //   return true;
  // }

  // async changePassword(oldPassword: string, newPassword: string) {
  //   const [res, err] = await authApi.updatePassword({
  //     password_new: newPassword,
  //     password_old: oldPassword
  //   });

  //   if (err) {
  //     if (err.response?.status != 400) {
  //       console.error('Account:Auth :: Invalid response code');
  //       throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
  //     }
  //     if (err.response?.data) {
  //       let messages = <TServerDefaultResponse>err.response.data;
  //       throw messages;
  //     }
  //     return false;
  //   }
  //   return true;
  // }

  // async startPasswordReset(email: string) {
  //   const [res, err] = await authApi.initiatePasswordRestore({ email });

  //   if (err) {
  //     console.error('Account:Auth :: Invalid response code');
  //     if (err.response?.data) {
  //       let messages = <TServerDefaultResponse>err.response.data;
  //       throw messages;
  //     }
  //     return false;
  //   }
    
  //   return true;
  // }


  // async checkPasswordResetToken(token: string) {
  //   const [res, err] = await authApi.checkPasswordRestoreToken({
  //     restore_code: token
  //   });

  //   if (err) {
  //     if (err.response?.status != 400) {
  //       console.error('Account:Auth :: Invalid response code');
  //       throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
  //     }
  //     if (err.response?.data) {
  //       let messages = <TServerDefaultResponse>err.response.data;
  //       throw messages;
  //     }
  //     return false;
  //   }
  //   return true;
  // }


  // async changePasswordByResetToken(token: string, newPassword: string) {
  //   const [res, err] = await authApi.completeRestorePassword({
  //     restore_code: token,
  //     password_new: newPassword
  //   });

  //   if (err) {
  //     if (err.response?.status != 400) {
  //       console.error('Account:Auth :: Invalid response code');
  //       throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
  //     }
  //     if (err.response?.data) {
  //       let messages = <TServerDefaultResponse>err.response.data;
  //       throw messages;
  //     }
  //     return false;
  //   }
  //   return true;
  // }


  // async register(email: string, password: string) {
  //   const [res, err] = await authApi.registerAccount({ email, password });

  //   if (err) {
  //     if (err.response?.status != 400) {
  //       console.error('AccountDTO :: Invalid response code');
  //       throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
  //     }
  //     if (err.response?.data) {
  //       let messages = <TServerDefaultResponse>err.response.data;
  //       throw messages;
  //     }
  //     return false;
  //   }

  //   await CSRFTokenService.refreshCSRFToken();
  //   this.loadAccountDTO();
  //   return true;
  // }

}