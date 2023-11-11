import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import Home from '@/pages/Static/Home.vue';
import Page404 from '@/pages/Static/404.vue';

import AccountStore from '@/models/Account';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'static-home',
    component: Home,
  },
  {
    path: '/rent-analyzer/:address?/:options?',
    name: 'rent-estimator',
    component: () => import(/* webpackChunkName: "rentEstimator" */ '../pages/RentEstimator/index.vue'),
  },
  {
    path: '/search/:typeOptions/:options?/:sort?',
    name: 'search',
    component: () => import(/* webpackChunkName: "search" */ '../pages/Search/index.vue'),
  },
  {
    path: '/price',
    name: 'static-price',
    component: () => import(/* webpackChunkName: "price" */ '../pages/Static/Price.vue'),
  },
  {
    path: '/aboutus',
    name: 'static-about-us',
    component: () => import(/* webpackChunkName: "aboutUs" */ '../pages/Static/AboutUs.vue'),
  },
  {
    path: '/contact-us',
    name: 'static-contact-us',
    component: () => import(/* webpackChunkName: "aboutUs" */ '../pages/Static/ContactUs.vue'),
  },
  {
    path: '/howitworks',
    name: 'static-how-it-works',
    component: () => import(/* webpackChunkName: "howItWorks" */ '../pages/Static/HowItWorks.vue'),
  },
  {
    path: '/whatwedo',
    name: 'static-what-we-do',
    component: () => import(/* webpackChunkName: "whatWeDo" */ '../pages/Static/WhatWeDo.vue'),
  },
  {
    path: '/terms-of-use',
    name: 'static-terms-and-conditions',
    component: () => import(/* webpackChunkName: "termsAndConditions" */ '../pages/Static/TermsAndConditions.vue'),
  },
  {
    path: '/privacy-policy',
    name: 'static-privacy-policy',
    component: () => import(/* webpackChunkName: "privacyPolicy" */ '../pages/Static/PrivacyPolicy.vue'),
  },
  {
    path: '/account',
    name: 'account',
    component: () => import(/* webpackChunkName: "account" */ '../pages/Account/index.vue'),
    children: [
      {
        path: 'subscription',
        name: 'account-subscriptions',
        component: () => import(/* webpackChunkName: "account" */ '../pages/Account/Subscription.vue')
      },
      {
        path: 'settings',
        name: 'account-settings',
        component: () => import(/* webpackChunkName: "account" */ '../pages/Account/AccountSettings.vue')
      },
      {
        path: 'email-settings',
        name: 'account-email-settings',
        component: () => import(/* webpackChunkName: "account" */ '../pages/Account/EmailSettings.vue')
      },
      {
        path: 'favorites',
        name: 'account-favorites',
        component: () => import(/* webpackChunkName: "account" */ '../pages/Account/Favorites.vue')
      },
      {
        path: 'reports',
        name: 'account-reports',
        component: () => import(/* webpackChunkName: "account" */ '../pages/Account/Reports.vue')
      },
      {
        path: 'subscription-cancel',
        name: 'account-cancel-subscription',
        component: () => import(/* webpackChunkName: "account" */ '../pages/Account/CancelSubscription.vue')
      }
    ]
  },
  {
    path: '/property/:id/:financialProps?',
    name: 'property',
    component: () => import(/* webpackChunkName: "property" */ '../pages/Property/index.vue')
  },

  /** SEMI-STATIC MESSAGES */
  {
    path: '/msg/payment-success/:tid?/:revenue?/:pid?',
    name: 'static-payment-success',
    component: () => import(/* webpackChunkName: "msg-payments-status" */ '../pages/Static/ThankYouPage.vue'),
  },
  {
    path: '/msg/payment-fail/:message?',
    name: 'static-payment-fail',
    component: () => import(/* webpackChunkName: "msg-payments-status" */ '../pages/Static/PaymentFail.vue'),
  },
  {
    path: '/msg/email-confirm-issue/:message?',
    name: 'static-email-confirmation-fail',
    component: () => import(/* webpackChunkName: "msg-emailConfirmation-fail" */ '../pages/Static/EmailConfirmationFail.vue'),
  },
  {
    path: '/msg/email-confirm-ok',
    name: 'static-email-confirmation-success',
    component: () => import(/* webpackChunkName: "msg-emailConfirmation-success" */ '../pages/Static/EmailConfirmationSuccess.vue'),
  },
  {
    path: '/restore-password/:token',
    name: 'static-reset-password',
    component: () => import(/* webpackChunkName: "msg-reset-password" */ '../pages/Static/PasswordReset.vue'),
  },
  {
    path: '/accept-terms-of-use',
    name: 'static-accept-terms-and-conditions',
    component: () => import(/* webpackChunkName: "termsAndConditions" */ '../pages/Static/AcceptTermsOfUse.vue'),
  },



  /** 404 CATCH ALL OTHER */

  {
    path: '/:path(.*)*',
    alias: '/404-not-found/:path(.*)*',
    name: 'static-not-found',
    component: Page404,
  },
];

if (process.env.NODE_ENV == 'development') {
  routes.push({
    path: '/ui',
    name: 'ui-demo',
    component: () => import(/* webpackChunkName: "ui-demo" */ '../pages/UIDemo.vue'),
  });
  routes.push({
    path: '/ui-icons',
    name: 'ui-icons',
    component: () => import(/* webpackChunkName: "ui-icons" */ '../pages/UIIcons.vue'),
  });
  routes.push({
    path: '/blog',
    name: 'static-blog',
    component: () => import(/* webpackChunkName: "blog" */ '../pages/Static/Blog.vue'),
  });
}

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    document.body.classList.remove('no-scroll');

    
    if (to.name == 'search' && savedPosition) {
      document.body.setAttribute('data-scroll-top', savedPosition.top.toString());
    }

    // always scroll to top
    return { top: 0 }
  },
});

router.beforeEach(async (to, from, next) => {
  // Wait untill AccountStore is READY
  await AccountStore.Auth.initPromise;

  // Accept Terms of use Guard
  if (AccountStore.Auth.isLoggedIn && AccountStore.Basis.dto?.warnings.includes('terms_of_use_not_accepted'))
    if (to.name != 'static-accept-terms-and-conditions' && to.name != 'static-terms-and-conditions')
      return next({ name: 'static-accept-terms-and-conditions' });

  // // Accept Terms of use Guard
  // if (AccountStore.Auth.isLoggedIn && AccountStore.Basis.dto?.warnings.includes('change_password_requested'))
  //   if (to.name != 'static-accept-terms-and-conditions' && to.name != 'static-terms-and-conditions')
  //     return next({ name: 'static-accept-terms-and-conditions' });
      
  next();
});

router.afterEach((to: any, from: any) => {
  if (from.name == 'search' || from.name == 'rent-estimator') {
    localStorage.removeItem('ofirio-saved-after-login-data-after-login');
    localStorage.removeItem('ofirio-saved-after-login-active');
  }

  const doNotSaveRouteList = [
    'static-payment-success',
    'static-payment-fail',
    'static-email-confirmation-fail',
    'static-email-confirmation-success',
    'static-reset-password',
    'static-accept-terms-and-conditions'
  ];

  if (!doNotSaveRouteList.includes(to.name))
    localStorage.setItem('ofirio-saved-after-login-url', JSON.stringify({ name: to.name, params: to.params, query: to.query }));
})

export default router;
