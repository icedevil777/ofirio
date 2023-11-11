from django.db import models


class SpinTextCache(models.Model):
    ''' this is a common cache for portal, stage and master.
        model exists in `prop_db` (not `default`) and is managed by playground
    '''
    text_key = models.CharField(primary_key=True, max_length=255)
    variables = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'spin_text_cache'
        managed = False


class PlaceStat(models.Model):
    place = models.CharField(primary_key=True, max_length=128)
    data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'place_stat'
        managed = False
