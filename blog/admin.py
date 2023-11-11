from django.contrib import admin

from blog.models import ArticleViewCounter


class ArticleViewCounterAdmin(admin.ModelAdmin):
    model = ArticleViewCounter

admin.site.register(ArticleViewCounter, ArticleViewCounterAdmin)
