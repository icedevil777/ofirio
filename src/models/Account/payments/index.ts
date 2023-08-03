import { AccountStoreType } from '@/models/Account';
import { loadStripe } from '@stripe/stripe-js';

import API, { TAccountDTO__Client_QuizData, TAccountDTO__Client_Subscription_Periods, TAccountDTO__QuizData, TAccountDTO__Subscriptions } from './api';
import VueStore from 'vue-class-store';
import { APP_DEFAULT_SMTH_BAD_FROM_SERVER, APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED } from '@/constants/DefaultMessages';
import paymentPrice from './paymentPrice';

let Account: AccountStoreType;

@VueStore
export default class AccountSubscriptionsModule {

  private stripeBusy: boolean = false;

  private _dto: TAccountDTO__Subscriptions | null = null;
  private _quizDTO: TAccountDTO__QuizData | null = null;
  public quizAnswersDTO: TAccountDTO__Client_QuizData | null = null;

  constructor(AccountRef: AccountStoreType) {
    Account = AccountRef;
  }

  public get dto() {
    return this._dto;
  }

  public get quizDTO() {
    return this._quizDTO;
  }

  public async load() {

    this._dto = null;
    const [res, err] = await API.loadSubscriptions();

    if (err) {
      if (![401, 404].includes(<number>err.response?.status)) {
        console.error('Account:Subscriptions :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
      }
      
      if (<number>err.response?.status == 404)
        return true;

      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return false;
    }

    this._dto = res.data;
    return true;
  }


  public async startSubscription(period: TAccountDTO__Client_Subscription_Periods) {
    if (this.stripeBusy)
      return;
    
    if (!this.isPayable(period))
      return;
    
    this.stripeBusy = true;
    
    const [res, err] = await API.startSubscription({ period });

    if (err) {
      if (![401].includes(<number>err.response?.status)) {
        console.error('Account:Subscriptions :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
      }

      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return false;
    }

    const stripe = await loadStripe(res.data.stripe_publishable_key);
    stripe?.redirectToCheckout({ sessionId: res.data.stripe_session_id });

    return true;
  }

  public async changePaymentMethod() {
    const [res, err] = await API.changePaymentMethod();

    if (err) {
      if (![401, 400].includes(<number>err.response?.status)) {
        console.error('Account:Subscriptions :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
      }

      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return false;
    }

    const stripe = await loadStripe(res.data.stripe_publishable_key);
    stripe?.redirectToCheckout({ sessionId: res.data.stripe_session_id });

    return true;
  }

  public async stopSubscription(reason: string) {
    const [res, err] = await API.cancelSubscription({ user_cancel_reason: reason });

    if (err) {
      if (![401, 400].includes(<number>err.response?.status)) {
        console.error('Account:Subscriptions :: Invalid response code');
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

  public async loadQuiz() {
    const [res, err] = await API.loadQuiz();

    if (err) {
      if (![401].includes(<number>err.response?.status)) {
        console.error('Account:Subscriptions :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER_WRAPPED;
      }

      if (err.response?.data) {
        let messages = <TServerDefaultResponse>err.response.data;
        throw messages;
      }
      return false;
    }

    this._quizDTO = res.data;

    this.quizAnswersDTO = {};
    for (let qz of this._quizDTO.quiz)
      this.quizAnswersDTO[qz.name] = '';

    return true;
  }

  public async saveQuiz() {
    if (!this.quizAnswersDTO)
      return;

    const [res, err] = await API.sendQuiz(this.quizAnswersDTO);

    if (err) {
      if (![401].includes(<number>err.response?.status)) {
        console.error('Account:Subscriptions :: Invalid response code');
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

  public isPayable(plan: TAccountDTO__Client_Subscription_Periods) {
    const current:TAccountDTO__Client_Subscription_Periods | undefined = <TAccountDTO__Client_Subscription_Periods>Account.Basis.dto?.subscription.period;

    if (Account.Basis.isPremium === false)
      return true;

    if (!current)
      return;
      
    const indexNow = paymentPrice.findIndex((price) => price.type == current);
    const indexNext = paymentPrice.findIndex((price) => price.type == plan);

    if (indexNext <= indexNow)
      return false;

    return true;
  }

  public async previewUpgrade(plan: TAccountDTO__Client_Subscription_Periods) {

    if (Account.Basis.isPremium === false || !this.isPayable(plan) || Account.Basis.dto?.is_team)
      return undefined;
      
    const [res, err] = await API.upgradePreview({ period: plan });
    if (err) {
      if (![400, 401].includes(<number>err.response?.status)) {
        console.error('Account:previewUpgrade :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER;
      }
    }
    return res.data;
  }

  public async upgrade(plan: TAccountDTO__Client_Subscription_Periods) {

    if (Account.Basis.isPremium === false || !this.isPayable(plan))
      return false;
      
    const [res, err] = await API.upgrade({ period: plan });
    if (err) {
      if (![400, 401].includes(<number>err.response?.status)) {
        console.error('Account:Upgrade :: Invalid response code');
        throw APP_DEFAULT_SMTH_BAD_FROM_SERVER;
      }
    }

    return true;
  }

}