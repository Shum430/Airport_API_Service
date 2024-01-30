from django.db.models import Count, F
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from airport.models import (
    Crew,
    Country,
    Passenger,
    Airport,
    Airplane,
    Route,
    Order,
    Flight,
    AirplaneType
)
from airport.serializers import (
    CrewSerializer,
    CountrySerializer,
    PassengerSerializer,
    AirportSerializer,
    AirplaneSerializer,
    RouteSerializer,
    OrderSerializer,
    FlightSerializer,
    AirplaneTypeSerializer,
    CrewDetailSerializer,
    CrewListSerializer,
    FlightDetailSerializer,
    FlightListSerializer, OrderListSerializer,
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        if self.action == "retrieve":
            return CrewDetailSerializer
        return CrewSerializer

    def get_queryset(self):
        queryset = (
            Crew.objects
            .prefetch_related("flights__route", "flights__airplane", "flights__airplane__airplane_type", "flights")
        )

        return queryset


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer



class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset.select_related("country")
        return queryset

class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset.select_related("airplane_type")
        return queryset


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset.select_related("source", "destination")
        return queryset


class OrderPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination

    def get_queryset(self):
        queryset = self.queryset.filter(passenger=self.request.user)

        if self.action == "list":
            queryset = (
                queryset
                .select_related("passenger")
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(passenger=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset = (
                queryset
                .select_related("airplane", "route")
                .prefetch_related("crew")
                .annotate(seats_available=F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets"))
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer
