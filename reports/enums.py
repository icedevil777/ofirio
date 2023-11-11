from django.db import models


class ReportType(models.TextChoices):
    RENT_ANALYZER = 'rent_analyzer', 'Rent Analyzer'
    PROPERTY = 'property', 'Property'
