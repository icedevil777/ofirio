import axios from 'axios';
import { of } from 'await-of';

export type TAccountDTO__SubscriptionItem = {
  number: string,
  period_end: string,
  period_start: string,
  created: string,
  total: number,
  invoice_url: string,
  plan_description: string
}

export type TAccountDTO__Subscriptions = {
  current_period_start: string,
  current_period_end: string,
  status: string,
  invoices: Array<TAccountDTO__SubscriptionItem>,
  card_last_4: string,
  next_payment_amount: number,
  cancel_at_period_end: boolean
}

export type TAccountDTO__Client_Subscription_Periods = 'month'|'quarter'|'year';
export type TAccountDTO__Client_SubscriptionType = {
  period: TAccountDTO__Client_Subscription_Periods
}

export type TAccountDTO__SubscriptionStartData = {
  stripe_session_id: string,
  stripe_publishable_key: string
}

export type TAccountDTO__Client_SubscriptionCancel = {
  user_cancel_reason: string
}

export type TAccountDTO__QuizData_Row_Answer = {
  value: string,
  type: 'checkbox' | 'textarea'
}

export type TAccountDTO__QuizData_Row = {
  name: string,
  question: string,
  answers: Array<TAccountDTO__QuizData_Row_Answer>
}

export type TAccountDTO__QuizData = {
  quiz: Array<TAccountDTO__QuizData_Row>
}

export type TAccountDTO__Client_QuizData = Record<string, string>

export type TAccountDTO__SubscriptionUpgradePreview = {
  description: string,
  currency: string,
  total: number,
  card_brand: string,
  card_exp_month: number,
  card_exp_year: number,
  card_last_4: string,
  period_end: string,
  period_start: string
}



export default {
  loadSubscriptions: function () {
    return <AxiosRequestToAwaiting<TAccountDTO__Subscriptions>>of(axios.get(`/api/account/subscription`));
  },

  startSubscription: function (data: TAccountDTO__Client_SubscriptionType) {
    return <AxiosRequestToAwaiting<TAccountDTO__SubscriptionStartData>>of(axios.post(`/api/subscription/start`, data));
  },

  changePaymentMethod: function() {
    return <AxiosRequestToAwaiting<TAccountDTO__SubscriptionStartData>>of(axios.post(`/api/subscription/change-payment-method-start`));
  },

  loadQuiz: function () {
    return <AxiosRequestToAwaiting<TAccountDTO__QuizData>>of(axios.get(`/api/subscription/quiz`));
  },

  sendQuiz: function (data: TAccountDTO__Client_QuizData) {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`/api/subscription/quiz`, data));
  },

  cancelSubscription: function (data: TAccountDTO__Client_SubscriptionCancel) {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`/api/subscription/cancel`, data));
  },

  upgrade: function (data: TAccountDTO__Client_SubscriptionType) {
    return <AxiosRequestToAwaiting<void>>of(axios.post(`/api/subscription/upgrade`, data));
  },

  upgradePreview: function (data: TAccountDTO__Client_SubscriptionType) {
    return <AxiosRequestToAwaiting<TAccountDTO__SubscriptionUpgradePreview>>of(axios.post(`/api/subscription/upgrade-preview`, data));
  }
}