import Account from '@/models/Account';

export default async function () {
  await Promise.allSettled([
    Account.Auth.loadAccountDTO(),
    Account.Auth.getSocialLoginUrls()
  ]);
}