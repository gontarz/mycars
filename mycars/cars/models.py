from django.db import models


# from django.contrib.postgres.fields import ArrayField


class Car(models.Model):
    make = models.CharField(max_length=30)
    model = models.CharField(max_length=30)

    class Meta:
        unique_together = ('make', 'model')


class Rating(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    rating = models.IntegerField()
