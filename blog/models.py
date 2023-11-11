from django.db import models

from common.models import BaseModel


class ArticleViewCounterManager(models.Manager):

    def increase(self, article_id):
        counter, _ = self.get_or_create(article_id=article_id)
        counter.count += 1
        counter.save()

        return counter.count



class ArticleViewCounter(BaseModel):
    objects = ArticleViewCounterManager()

    article_id = models.IntegerField(unique=True)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f'article_id={self.article_id}, count={self.count}'
