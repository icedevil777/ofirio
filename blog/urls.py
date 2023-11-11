from django.urls import path

from . import views


app_name = 'blog'
urlpatterns = [
    path('api/blog/home/', views.HomeView.as_view(), name='home'),
    path('api/blog/tab/', views.TabView.as_view(), name='tab'),
    path('api/blog/articles/', views.ArticleListView.as_view(), name='article-list'),
    path('api/blog/articles/<slug:id_or_slug>/', views.ArticleView.as_view(), name='article-detail'),
    path('api/blog/authors/<slug:id_or_slug>/', views.AuthorView.as_view(), name='author-detail'),
    path('api/blog/categories/<slug:id_or_slug>/', views.CategoryView.as_view(), name='category-detail'),
    path('api/blog/slugs/', views.SlugsView.as_view(), name='slugs'),
]
