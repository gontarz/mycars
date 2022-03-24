import requests
from rest_framework.test import APITestCase

from rest_framework import status
from unittest.mock import patch, Mock
from cars.models import Car, Rating


class E2ETests(APITestCase):
    def test_create_car(self):
        """
        Ensure we can create a new car object (trigger http request to external API - vpic).
        """
        data = {"make": "Volkswagen", "model": "Golf"}

        self.client.post('/cars/', data, format='json')
        Car.objects.get(make='volkswagen', model='golf')

        self.assertEqual(Car.objects.count(), 1)

    def test_create_car_fails_make_missing_in_vpic(self):
        data = {"make": "missing make", "model": "golf"}

        response = self.client.post('/cars/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_car_fails_model_missing_in_vpic(self):
        data = {"make": "Volkswagen", "model": "missing model"}

        response = self.client.post('/cars/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CarsTests(APITestCase):
    @staticmethod
    def _mocked_requests_get_success():
        mocked_response = Mock(spec_set=requests.Response)
        mocked_response.json = lambda: {
            'Count': 1,
            'Message': 'Response returned successfully',
            'SearchCriteria': 'Make:volkswagen',
            'Results': [{'Make_ID': 482, 'Make_Name': 'VOLKSWAGEN', 'Model_ID': 3134, 'Model_Name': 'Passat'}]}
        return Mock(spec_set=requests.get, return_value=mocked_response)

    @staticmethod
    def _mocked_requests_get_empty():
        mocked_response = Mock(spec_set=requests.Response)
        mocked_response.json = lambda: {'Count': 0, 'Message': 'Response returned successfully',
                                        'SearchCriteria': 'Make:gffsdfsdfs', 'Results': []}
        return Mock(spec_set=requests.get, return_value=mocked_response)

    @patch("requests.get", _mocked_requests_get_success())
    def test_create_car(self):
        data = {"make": "Volkswagen", "model": "Passat"}

        response = self.client.post('/cars/', data, format='json')
        car = Car.objects.get(make='volkswagen', model='passat')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {'id': car.id, 'make': 'volkswagen', 'model': 'passat', 'avg_rating': None}
        )
        self.assertEqual(Car.objects.count(), 1)

    @patch("requests.get", _mocked_requests_get_empty())
    def test_create_car_fails_make_missing_in_vpic(self):
        data = {"make": "missing make", "model": "passat"}

        response = self.client.post('/cars/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("requests.get", _mocked_requests_get_success())
    def test_create_car_fails_model_missing_in_vpic(self):
        data = {"make": "Volkswagen", "model": "missing model"}

        response = self.client.post('/cars/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_cars(self):
        car1 = Car.objects.create(**{'make': 'volkswagen', 'model': 'golf'})
        car2 = Car.objects.create(**{'make': 'volkswagen', 'model': 'passat'})

        response = self.client.get('/cars/', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'],
            [
                {'id': car1.id, 'make': 'volkswagen', 'model': 'golf', 'avg_rating': None},
                {'id': car2.id, 'make': 'volkswagen', 'model': 'passat', 'avg_rating': None}
            ]
        )

    def test_delete_car(self):
        car = Car.objects.create(**{'make': 'volkswagen', 'model': 'golf'})

        response = self.client.delete(f'/cars/{car.id}/', format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Car.objects.count(), 0)


class RatingTests(APITestCase):
    def setUp(self):
        self.car = Car.objects.create(**{'make': 'volkswagen', 'model': 'golf'})

    def test_create_rating(self):
        """
        Ensure we can add a rating.
        """
        data = {"car_id": self.car.id, "rating": 5}

        response = self.client.post('/rate/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, data)

    def test_get_avg_rating(self):
        data1 = {"car_id": self.car.id, "rating": 5}
        data2 = {"car_id": self.car.id, "rating": 2}

        self.client.post('/rate/', data1, format='json')
        self.client.post('/rate/', data2, format='json')
        response = self.client.get('/cars/', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['avg_rating'], 3.5)

    def test_create_rating_fails_rating_minimum(self):
        data1 = {"car_id": self.car.id, "rating": 0}

        response = self.client.post('/rate/', data1, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rating_fails_rating_maximum(self):
        data1 = {"car_id": self.car.id, "rating": 6}

        response = self.client.post('/rate/', data1, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PopularTests(APITestCase):
    def setUp(self):
        self.car1 = Car.objects.create(**{'make': 'volkswagen', 'model': 'golf'})
        self.car2 = Car.objects.create(**{'make': 'volkswagen', 'model': 'passat'})
        Rating.objects.create(rating=1, car=self.car1)
        Rating.objects.create(rating=5, car=self.car1)
        Rating.objects.create(rating=5, car=self.car2)

    def test_list_popular(self):
        response = self.client.get('/popular/', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'],
            [
                {'id': self.car1.id, 'make': 'volkswagen', 'model': 'golf', 'rates_number': 2},
                {'id': self.car2.id, 'make': 'volkswagen', 'model': 'passat', 'rates_number': 1}
            ]
        )
