from __future__ import unicode_literals

from django.db import models


class DataPoint(models.Model):
    bedroom_temperature = models.FloatField("Bedroom Temperature")
    bedroom_humidity = models.FloatField("Bedroom Humidity")
    datetime = models.DateTimeField()
