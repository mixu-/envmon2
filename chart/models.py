from __future__ import unicode_literals
from django.core.validators import MaxValueValidator, MinValueValidator

from django.db import models


class DataPoint(models.Model):
    bedroom_temperature = models.\
        FloatField("Bedroom Temperature", validators=\
           [MaxValueValidator(60, "Temperature above maximum (60C)!"),
            MinValueValidator(0, "Temperature below minimum (0C)!")])

    bedroom_humidity = models.FloatField("Bedroom Humidity", validators=\
        [MaxValueValidator(100, "Humidity above maximum (100%)!"),
         MinValueValidator(0, "Humidity below minimum (0%)!")])

    datetime = models.DateTimeField()
