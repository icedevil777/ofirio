import AccountProfileModule from './profile';
import AccountBasisModule from './basis';
import AccountAuthModel from './auth';
import AccountFavoritesModule from './favorites';
import AccountEmailSettingsModule from './email-settings';
import AccountSubscriptionsModule from './payments';
import AccountReportsModule from './reports';
import AccountRestrictionsModule from './restrictions';

export type AccountStoreType = {
  Basis: AccountBasisModule,
  Auth: AccountAuthModel,
  Profile: AccountProfileModule,
  Favorites: AccountFavoritesModule,
  EmailSettings: AccountEmailSettingsModule,
  Subscriptions: AccountSubscriptionsModule,
  Reports: AccountReportsModule,
  Restrictions: AccountRestrictionsModule
}

const Account: AccountStoreType = <AccountStoreType>{};
Account.Auth = new AccountAuthModel(Account);
Account.Basis = new AccountBasisModule(Account);
Account.Profile = new AccountProfileModule(Account);
Account.Favorites = new AccountFavoritesModule(Account);
Account.EmailSettings = new AccountEmailSettingsModule(Account);
Account.Subscriptions = new AccountSubscriptionsModule(Account);
Account.Reports = new AccountReportsModule(Account);
Account.Restrictions = new AccountRestrictionsModule(Account);

export default Account;