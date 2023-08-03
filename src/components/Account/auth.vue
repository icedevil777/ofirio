<template>
  <div class="container">

    <UMessageList ref="messageList" :maxCount="4" />
    <form class="login" v-if="state == 'login'" @submit.prevent.stop>
      <h1>Login to Account</h1>
      <div class="oauth flex">
        <UButton class="ui-btn-iconic ui-btn-circle" @click="actionLoginSocial('facebook')"><UIcon name="facebook-circle"/>Facebook</UButton>
        <UButton class="ui-btn-iconic ui-btn-circle" @click="actionLoginSocial('google')"><UIcon name="google"/>Google</UButton>
      </div>
      <UDivider label="OR" />
      <UFloatingInput v-model="authData.email" class="email" label="E-mail" type="email" required :scheme="validators.VEmail"/>
      <UFloatingInput v-model="authData.password" class="password" label="Password" type="password" required :scheme="validators.VPassword"/>
      <div class="ui-text-right forgot-password">
        <UButton class="ui-btn-text ui-btn-text-gray" @click="setState('reset')">Forgot password?</UButton>
      </div>
      <UButton
        class="ui-btn ui-btn-green auth-popup-btn"
        :busy="inProgressState"
        @click="actionLogin"
      >Login</UButton>
      <div class="ui-text-center not-a-member-yet">Not a member yet?</div>
      <UButton
        class="ui-btn ui-btn-bordered-green auth-popup-btn"
        @click="setState('register')"
      >Register for FREE</UButton>
      <UDivider />
      <div class="ui-text-center terms">
        By login you agree to Ofirio’s
        <router-link :to="{ name: 'static-terms-and-conditions' }">
          <a @click="() => $root['ev-popup-login-close']()" class="ui-href ui-href-underline">Terms of Use</a>
        </router-link>
        and<br> 
        <router-link :to="{ name: 'static-privacy-policy' }">
          <a @click="() => $root['ev-popup-login-close']()" class="ui-href ui-href-underline">Privacy Policy</a>
        </router-link>
      </div>
      <div class="secure-area">
        <UIcon name="lock-circle" /> Secure area
      </div>
    </form>


    <form class="register" v-if="state == 'register'" @submit.prevent.stop>
      <h1>Subscribe to Ofirio</h1>
      <div class="oauth flex">
        <UButton class="ui-btn-iconic ui-btn-circle" @click="actionLoginSocial('facebook')"><UIcon name="facebook-circle"/>Facebook</UButton>
        <UButton class="ui-btn-iconic ui-btn-circle" @click="actionLoginSocial('google')"><UIcon name="google"/>Google</UButton>
      </div>
      <UDivider label="OR" />
      <UFloatingInput v-model="authData.email" class="email" label="E-mail" type="email" required :scheme="validators.VEmail"/>
      <UFloatingInput v-model="authData.password" class="password" label="Password" type="password" required :scheme="validators.VPassword"/>
      <PasswordStrength :passmodel="authData.password" />
      <div class="agreement-confirmation">
        <UCheckboxInput v-model="authData.agree">
          <span>
            I agree to OFIRIO
            <router-link :to="{ name: 'static-terms-and-conditions' }">
              <a @click="() => $root['ev-popup-login-close']()" class="ui-href ui-href-underline">Terms &amp; Conditions</a>
            </router-link>
          </span>
        </UCheckboxInput>
      </div>
      <UButton
        class="ui-btn ui-btn-green auth-popup-btn"
        :busy="inProgressState"
        @click="actionRegister"
      >Get Started</UButton>
      <div class="ui-text-center already-a-member">Already a member? <span class="ui-href ui-href-underline" @click="setState('login')">Login</span></div>
      <UDivider class="hide-desktop" />
      <div class="secure-area">
        <UIcon name="lock-circle" /> Secure area
      </div>
    </form>


    <form class="reset" v-else-if="state == 'reset'" @submit.prevent.stop>
      <h1>Reset password</h1>
      <div class="desc">We'll send you a link to email so you can reset your password.</div>
      <UFloatingInput v-model="authData.email" class="email" label="E-mail" type="email" required :scheme="validators.VEmail"/>
      <UButton
        class="ui-btn ui-btn-green btn-reset auth-popup-btn"
        @click="actionResetPassword"
      >Send an E-mail</UButton>
      <div class="ui-text-center">
        <UButton
          class="ui-btn-text ui-btn-text-gray"
          @click="setState()"
        >Cancel</UButton>
      </div>
    </form>


    <div class="reset-success" v-else-if="state == 'reset-success'">
      <h1>Reset password</h1>
      <div class="desc">We emailed instructions to <b>{{ authData.email }}</b>. Didn't receive it? Check your spam folder or <span class="ui-href ui-href-underline" @click="setState('reset')">send the email again</span>.</div>
      <div class="desc">Still having issues? Contact <a href="#" class="ui-href ui-href-underline">customer support</a>.</div>
      <UButton
        class="ui-btn ui-btn-green btn-back auth-popup-btn"
        @click="setState()"
      >Back to Login</UButton>
    </div>

    <div class="email-validation-required" v-else-if="state == 'email-validation'">
      <h1>Email validation required</h1>
      <div class="desc">We emailed a confirmation email to <b>{{ authData.email || Account.Basis.dto?.email }}</b>. Didn't receive it? Check your spam folder.</div>
      <div class="desc">Still having issues? Contact <a href="#" class="ui-href ui-href-underline">customer support</a>.</div>
    </div>


  </div>
</template>

<style lang="less" scoped>
.container {
  padding: 40px 100px;
  background: @col-bg;
  color: @col-text-gray-dark;
  line-height: 20px;

  > div, > form {
    h1 {
      font-size: 2rem;
      font-weight: 800;
      line-height: 2.5rem;
      color: @col-text-dark;
      margin-bottom: 30px;
      display: block;
      text-align: center;

      @media @mobile {
        font-size: 1.5rem;
        line-height: 2rem;
      }
    }
  }

  .oauth {
    justify-content: space-between;
    align-items: center;

    .ui-btn-iconic {
      @h: 50px;
      @bw: 1px;

      width: 48%;
      padding: 10px 30px;
      white-space: nowrap;
      box-shadow: none;
      line-height: @h;
      height: @h;
      border-radius: @h;
      border: @bw solid @col-gray-light;
      font-weight: bold;

      &::v-deep .svg-icon {
        fill: currentColor;
        width: 28px;
        min-width: 28px;
        height: 28px;
        min-height: 28px;
        margin-right: 10px
      }
    }
  }
  .ui-floating-input {
    display: block;
    margin-top: 20px;
    font-weight: 600;
  }
  .ui-divider {
    margin: 30px 0;
  }
  .auth-popup-btn {
    display: block;
    width: 100%;
    height: 50px;
    padding-top: 0;
    padding-bottom: 0;
    margin: 20px 0;
  }
  .desc {
    line-height: inherit;
    margin: 20px 0;
  }


  .login {
    .forgot-password {
      margin: 10px 0 20px;
      font-size: 0.875rem;
      
      .ui-button {
        font-weight: normal;
        text-decoration: underline;
      }
    }
    // .agreement-confirmation {
      // .ui-href { margin-left: 10px;}
    // }
    .terms {
      font-size: 0.875rem;
      line-height: 18px;
    }
  }
  .reset {
    .ui-btn-text-gray { text-decoration: underline; }
  }
  .reset-success {
    .desc b { color: @col-text-dark; }
    .ui-href-underline { cursor: pointer; }
  }
  .register {
    .no-credit-card { font-weight: 600; }
    .password-strength {
      margin-bottom: 20px;
    }
    .ui-href-underline { cursor: pointer; }
  }
  .secure-area {
    @h: 18px;
    @col: #767676;
    
    color: @col;
    line-height: @h;
    font-size: 0.875rem;
    display: none;
    text-align: center;
    margin-top: 20px;

    &::v-deep .svg-icon {
      fill: @col;
      stroke: @col;
      width: @h;
      height: @h;
      margin-right: @h/2;
      vertical-align: middle;
    }
    @media @mobile {
      display: block;
    }
  }
  @media @mobile {
    padding: 55px 20px 20px;
    // min-height: 100vh;
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';
import UButton from '@/components/ui/UButton.vue';
import UDivider from '@/components/ui/UDivider.vue';
import UCheckboxInput from '@/components/ui/UCheckboxInput.vue';
import UFloatingInput from '@/components/ui/UFloatingInput.vue';
import UMessageList from '@/components/ui/UMessageList.vue';
import PasswordStrength from './password-strength.vue';

import AccountStore from '@/models/Account';
import CSRFTokenService from '@/services/CSRFToken.service';
import { VAuthData, VEmail, VPassword } from '@/models/yups.model';
import { observe } from '@/services/LocalstorageWatcher.service';

type AuthState = 'login'|'register'|'reset'|'reset-success'|'email-validation';

export default defineComponent({
  components: {
    UButton,
    UDivider,
    UCheckboxInput,
    UFloatingInput,
    UMessageList,
    PasswordStrength
  },
  data() {
    return {
      inProgressState: false,
      state: 'login' as AuthState,
      authData: {
        email: '',
        password: '',
        agree: false
      },
      validators: {
        VEmail,
        VPassword
      }
    }
  },
  computed: {
    Account() {
      return AccountStore;
    }
  },
  methods: {
    __reset() {
      this.state = 'login';
    },
    reset(timeshift: number = 0) {
      if (timeshift == 0)
        this.__reset();
      else
        setTimeout(this.__reset, timeshift);
    },
    setState(state: AuthState = 'login') {
      this.authData.email = '';
      this.authData.password = '';
      this.state = state;
      (<any>this.$refs.messageList).reset();
    },

    processServerMessages(err: TServerDefaultResponse) {
      if (err.server_messages) {
        for (let msg of err.server_messages)
          (<any>this.$refs.messageList).push({
            type: msg.level,
            message: msg.message
          })
      }
      this.inProgressState = false;
    },

    async actionLogin() {
      if (this.inProgressState) return;

      this.inProgressState = true;

      VAuthData.validate(this.authData).then(() => {

        AccountStore.Auth.login(this.authData.email, this.authData.password).then(() => {
          this.inProgressState = false;
          this.$emit('login-success');
        }, (err) => this.processServerMessages(err));

      }).catch((ex:any) => {
        this.inProgressState = false;
        (<any>this.$refs).messageList.push({ message: ex.message, type: 'error' });
      });

    },

    async actionRegister() {
      if (this.inProgressState) return;

      this.inProgressState = true;

      VAuthData.validate(this.authData).then(() => {
        
        if (!this.authData.agree)
          throw new Error('You must accept our Terms & Conditions');

        AccountStore.Auth.register(this.authData.email, this.authData.password).then(() => {
          this.inProgressState = false;

          const email = this.authData.email;
          this.setState('email-validation');
          this.authData.email = email;
        }, (err) => this.processServerMessages(err));

      }).catch((ex:any) => {
        this.inProgressState = false;
        (<any>this.$refs).messageList.push({ message: ex.message, type: 'error' });
      });
    },

    async actionResetPassword() {
      if (this.inProgressState) return;

      this.inProgressState = true;

      VEmail.validate(this.authData.email).then(() => {

        AccountStore.Auth.startPasswordReset(this.authData.email).then(() => {
          this.inProgressState = false;
          const email = this.authData.email;
          this.setState('reset-success');
          this.authData.email = email;
        }, (err) => this.processServerMessages(err));

      }).catch((ex:any) => {
        this.inProgressState = false;
        (<any>this.$refs).messageList.push({ message: ex.message, type: 'error' });
      });

    },


    async actionLoginSocial(type: string) {
      if (this.inProgressState)
        return;

      if (!AccountStore.Auth.socialLoginUrls)
        return (<any>this.$refs).messageList.push({ type: 'error', message: 'Login by social account is temporarily inaccessible' });

      let loginPopover = window.open(AccountStore.Auth.socialLoginUrls[type], '_blank', 'toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes');
      
      let watchSuccess = observe('ofirio-account-social-logged-in', async () => {
        watchSuccess();
        
        await CSRFTokenService.refreshCSRFToken();
        this.Account.Auth.loadAccountDTO().then(() => {
          window.dataLayer = window.dataLayer || [];
          window.dataLayer.push({
            event: 'login_with_social',
            logInType: type,
            user_id: this.Account.Basis.dto?.pk
          });

          if (this.Account.Basis.dto?.warnings.includes('terms_of_use_not_accepted'))
            return this.$router.push({ name: 'static-accept-terms-and-conditions' });
        });
        (<any>this.$refs.messageList).push({
          type: 'success',
          message: 'Success'
        });
        this.$emit('login-success');
      });
      let watchFail = observe('ofirio-account-social-login-failed', () => {
        watchFail();
        (<any>this.$refs.messageList).push({
          type: 'error',
          message: 'Login with Auth2.0 failed'
        })
      });
    }



  }
  
})
</script>