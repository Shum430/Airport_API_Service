from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

from airport.models import Crew, Route, Airplane, Airport, AirplaneType, Country


class FlightTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@email.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)
        self.crew = Crew.objects.create(first_name='John', last_name='Doe')

        self.source_country = Country.objects.create(name='Source Country', population=1000000, net_worth=100000000)
        self.destination_country = Country.objects.create(name='Destination Country', population=1000000, net_worth=100000000)

        self.source_airport = Airport.objects.create(name='Source', country=self.source_country, closest_big_city='Source City')
        self.destination_airport = Airport.objects.create(name='Destination', country=self.destination_country, closest_big_city='Destination City')

        self.route = Route.objects.create(source=self.source_airport, destination=self.destination_airport, distance=100)
        self.airplane = Airplane.objects.create(name='Test Airplane', rows=10, seats_in_row=6, airplane_type=AirplaneType.objects.create(name='Test Type'))

    def tearDown(self):
        pass

    def test_flight_creation(self):
        flight_url = reverse("airport:flight-list")
        response = self.client.post(flight_url,
                                    {'crew': [self.crew.id], 'route': self.route.id, 'airplane': self.airplane.id,
                                     'departure_time': '2024-02-10T12:00:00Z', 'arrival_time': '2024-02-10T14:00:00Z'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_flight_list(self):
        flight_url = reverse("airport:flight-list")
        response = self.client.get(flight_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_flight_list_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        flight_url = reverse("airport:flight-list")
        response = self.client.get(flight_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
