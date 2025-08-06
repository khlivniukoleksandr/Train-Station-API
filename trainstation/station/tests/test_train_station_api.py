from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from station.models import Train, TrainType, Station, Order
from station.serializers import TrainSerializer, StationSerializer

TRAIN_URL = reverse("trainstation:train-list")
STATION_URL = reverse("trainstation:station-list")

def detail_url(train_id):
    return reverse("trainstation:train-detail", args=(train_id,))


def sample_train(**params) -> Train:
    defaults = {
        "name": "Train1",
        "cargo_num": 5,
        "places_in_cargo": 100,
    }
    defaults.update(params)
    return Train.objects.create(**defaults)

def sample_station(**params) -> Train:
    defaults = {
        "name": "Vasylkiv",
        "latitude": 49.4949,
        "longitude": 59.5959,
    }
    defaults.update(params)
    return Station.objects.create(**defaults)

class UnauthenticatedTrainApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_aut_required(self):
        response = self.client.get(TRAIN_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test",
            password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_trains_list(self):
        sample_train()
        train_with_type = sample_train()

        type1 = TrainType.objects.create(name="Intersity")
        train_with_type = sample_train(train_type=type1)

        response = self.client.get(TRAIN_URL)
        trains = Train.objects.all()
        serializer = TrainSerializer(trains, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_train_detail(self):
        type_obj = TrainType.objects.create(name="Intersity")
        train = sample_train(train_type=type_obj)

        url = detail_url(train.id)
        response = self.client.get(url)
        serializer = TrainSerializer(train)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_train_by_name(self):
        type_fast = TrainType.objects.create(name="Fast")
        type_slow = TrainType.objects.create(name="Slow")

        train1 = Train.objects.create(name="Express", train_type=type_fast, cargo_num=10, places_in_cargo=100)
        train2 = Train.objects.create(name="CargoMaster", train_type=type_slow, cargo_num=5, places_in_cargo=50)

        url = reverse("trainstation:train-list") + "?name=Expr"
        response = self.client.get(url)

        serializer_train1 = TrainSerializer(train1)
        serializer_train2 = TrainSerializer(train2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(dict(serializer_train1.data), [dict(item) for item in response.data["results"]])
        self.assertNotIn(serializer_train2, response.data["results"])



class UnauthenticatedStationApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_aut_required_station(self):
        response = self.client.get(STATION_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedStationApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_stations_list(self):
        sample_station()

        res = self.client.get(STATION_URL)
        stations = Station.objects.all()
        serializer = StationSerializer(stations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)


class StationPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="password123"
        )
        self.client.force_authenticate(self.user)

    def test_user_cannot_create_station(self):
        payload = {
            "name": "Vasylkiv",
            "latitude": 49.4949,
            "longitude": 59.5959,
        }
        res = self.client.post(STATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_station(self):
        admin_user = get_user_model().objects.create_superuser(
            email="admin@test.com",
            password="adminpass"
        )
        self.client.force_authenticate(admin_user)

        payload = {
            "name": "Vasylkiv",
            "latitude": 49.4949,
            "longitude": 59.5959,
        }
        res = self.client.post(STATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Station.objects.count(), 1)
        self.assertEqual(Station.objects.get().name, payload["name"])


class OrderVisibilityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            email="user1@test.com", password="pass123"
        )
        self.user2 = get_user_model().objects.create_user(
            email="user2@test.com", password="pass456"
        )


        self.order1 = Order.objects.create(user=self.user1)

        self.order2 = Order.objects.create(user=self.user2)

    def test_user_sees_only_own_orders(self):
        self.client.force_authenticate(self.user1)
        res = self.client.get(reverse("trainstation:order-list"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        order_ids = [order["id"] for order in res.data["results"]]
        self.assertIn(self.order1.id, order_ids)
        self.assertNotIn(self.order2.id, order_ids)











