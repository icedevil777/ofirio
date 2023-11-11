from django.urls import path

from . import views


app_name = 'account'

urlpatterns = [
    path('api/account', views.AccountView.as_view(), name='account'),
    path('api/account/login', views.JwtLoginView.as_view(), name ='login'),
    path('api/account/google-login', views.GoogleJwtLoginView.as_view(), name ='google_login'),
    path('api/account/facebook-login', views.FacebookJwtLoginView.as_view(), name ='facebook_login'),
    path('api/account/refresh', views.JwtRefreshView.as_view(), name='refresh'),
    path('api/account/logout', views.LogoutView.as_view(), name='logout'),

    # old login. We can't live without sessions anyway, admin panel wouldn't work then
    path('api/account/session-login', views.SessionLoginView.as_view(), name='session_login'),

    path('api/account/registration', views.RegistrationView.as_view(), name='registration'),
    path('api/account/resend_verification_email', views.ResendVerificationEmailView.as_view(), name='resend_verification_email'),
    path('api/account/verify_email/<slug:code>', views.VerifyEmailView.as_view(), name='verify_email'),

    path('api/account/change_profile', views.ChangeProfileView.as_view(), name='change_profile'),
    path('api/account/accept_terms_of_use', views.AcceptTermsOfUseView.as_view(), name='accept_terms_of_use'),

    path('api/account/change_password', views.ChangePasswordView.as_view(), name='change_password'),
    path('api/account/restore_password', views.RestorePasswordView.as_view(), name='restore_password'),
    path('api/account/restore_password_check', views.RestorePasswordCheckView.as_view(), name='restore_password_check'),
    path('api/account/restore_password_change', views.RestorePasswordChangeView.as_view(), name='restore_password_change'),
    path('api/account/email_settings', views.EmailSettingsView.as_view({'get': 'retrieve', 'post': 'update'}), name='email_settings'),
    path('api/account/good_deal_settings', views.GoodDealSettingsApiView.as_view({'get': 'retrieve', 'post': 'update'}), name='good_deal_settings'),

    path('api/account/limits-left', views.LimitsLeftView.as_view(), name='limits_left'),
    path('api/subscription/limits-left', views.LimitsLeftView.as_view(), name='old_limits_left'),  # deprecated
]
