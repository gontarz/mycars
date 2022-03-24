from rest_framework import serializers
import requests
from django.db.models import Avg, F

from cars.models import Car, Rating


class CarSerializer(serializers.ModelSerializer):
    make = serializers.CharField()
    model = serializers.CharField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = ['id', 'make', 'model', 'avg_rating']

    def create(self, validated_data):
        return Car.objects.create(**{k: v.lower() for k, v in validated_data.items()})

    def validate(self, data):
        """
        validate car in gov
        """
        response = requests.get(
            f"https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/{data['make'].lower()}?format=json").json()
        if response["Count"] == 0:
            raise serializers.ValidationError(f"Lack of car make: '{data['make']}' in government register")
        for result in response["Results"]:
            if data["model"].lower() == result["Model_Name"].lower():
                return data
        raise serializers.ValidationError(f"Lack of car model: '{data['model']}' in government register")

    def get_avg_rating(self, obj):
        return obj.rating_set.aggregate(avgs=Avg(F('rating'))).get('avgs', None)


class RatingSerializer(serializers.ModelSerializer):
    car_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Rating
        fields = ['rating', 'car_id']

    def create(self, validated_data):
        return Rating.objects.create(rating=validated_data["rating"], car=Car.objects.get(id=validated_data["car_id"]))


class PopularReadOnlySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    make = serializers.CharField()
    model = serializers.CharField()
    rates_number = serializers.IntegerField()

    class Meta:
        fields = ['id', 'make', 'model', 'rates_number']
        read_only_fields = fields
