from django.db.models import Count
from rest_framework import mixins, viewsets

from cars.models import Car, Rating
from cars.serializers import CarSerializer, RatingSerializer, PopularReadOnlySerializer


class CarViewSet(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    """
    Manage car data
    """
    queryset = Car.objects.all()
    serializer_class = CarSerializer


class RateViewSet(mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    """
    POST rating
    """
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


class PopularViewSet(mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """
    Generate and 'list' popular cars
    """
    queryset = Car.objects.annotate(rates_number=Count('rating')).order_by('-rates_number')[:10]
    serializer_class = PopularReadOnlySerializer
