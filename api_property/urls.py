from django.urls import path, re_path
from . import views


app_name = 'api_property'
urlpatterns = [
    path('api/building', views.BuildingView.as_view(), name='building'),
    path('api/building/recommendations', views.BuildingRecommendationsView.as_view(), name='building_recommendations'),

    path('api/property', views.Property.as_view(), name='property'),
    path('api/property/tax_history', views.TaxHistory.as_view(), name='tax_history'),
    path('api/property/prop_history', views.PropHistory.as_view(), name='prop_history'),
    path('api/property/schools', views.SchoolsView.as_view(), name='schools'),
    path('api/property/finance', views.FinanceView.as_view(), name='finance'),
    path('api/property/favorites', views.FavoriteView.as_view({'get': 'list', 'post': 'create'}),
         name='favorite'),
    path('api/property/favorites/<slug:identifier>', views.FavoriteView.as_view(
        {'delete': 'destroy'}), name='favorite_delete'),
    path('api/property/public_records', views.PublicRecordsView.as_view(), name='public_records'),
    path('api/property/analytics', views.Analytics.as_view(), name='analytics'),
    path('api/property/affordability', views.AffordabilityView.as_view(), name='affordability'),
    path('api/property/recommendations', views.Recommendations.as_view(), name='recommendations'),
    re_path(r'^api/property/dont_miss_property$', views.LastSearchDontMissProps.as_view(), name='dont_miss_property'),
    path('api/property/recently_viewed', views.RecentlyViewed.as_view(), name='recently_viewed'),
    re_path(r'^api/property/new_listings$', views.LastSearchNewListings.as_view(), name='new_listings'),
    re_path('^api/property/real_estate$', views.RealEstate.as_view(), name='real_etsate'),
    path('api/property/top_invest', views.TopInvestView.as_view(), name='top_invest'),
    path('api/property/similar_notifications', views.SimilarNotificationView.as_view(
        {'get': 'list', 'post': 'create'}), name='similar_notification'),
    path('api/property/similar_notifications/<int:pk>', views.SimilarNotificationView.as_view(
        {'delete': 'destroy'}), name='similar_notification_delete'),
    path('api/property/prop_updates_notifications', views.PropUpdatesView.as_view(
        {'get': 'list', 'post': 'create'}), name='prop_updates'),
    path('api/property/prop_updates_notifications/<int:pk>', views.PropUpdatesView.as_view(
        {'delete': 'destroy'}), name='prop_updates_delete'),

    # contact agent urls:
    path('api/property/rebate', views.RebateView.as_view(), name='rebate'),
    path('api/property/schedule_tour', views.ScheduleTourView.as_view(), name='schedule_tour'),
    path('api/property/ask_question', views.AskQuestionView.as_view(), name='ask_question'),
    path('api/property/check_availability', views.CheckAvailabilityView.as_view(), name='check_availability'),
    path('api/property/only_params_rebate', views.OnlyParamsRebateView.as_view(), name='only_params_rebate'),
    path('api/property/contact_sale_lp', views.ContactSaleLPView.as_view(), name='contact_sale_lp'),
    path('api/property/contact_for_help', views.GetHelpView.as_view(), name='contact_for_help')
]
