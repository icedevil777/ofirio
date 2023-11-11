from django.db import models


class BaseModel(models.Model):
    """
    Base model class for all the project models
    """
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
