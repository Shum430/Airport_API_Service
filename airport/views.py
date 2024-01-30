from django.db.models import Count, F
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

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
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
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
    FlightListSerializer, OrderListSerializer, AirplaneImageSerializer,
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        if self.action == "retrieve":
            return CrewDetailSerializer
        return CrewSerializer

    def get_queryset(self):
        queryset = (
            Crew.objects
            .prefetch_related(
                "flights",
                "flights__route",
                "flights__airplane",
                "flights__airplane__airplane_type",
            )
        )

        return queryset


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset.select_related("country")
        return queryset


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset.select_related("airplane_type")
        return queryset

    def get_serializer_class(self):
        if self.action == "upload_image":
            return AirplaneImageSerializer
        return AirplaneSerializer

    @action(methods=["POST"], detail=True, url_path="upload-image", permission_classes=[IsAdminUser])
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            (
                queryset
                .select_related("source", "destination")
                .prefetch_related(
                    "source__country",
                    "source__destination_routes",
                )
            )

        return queryset


class OrderPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

    def get_queryset(self):
        queryset = self.queryset.filter(passenger=self.request.user)

        if self.action == "list":
            queryset = (
                queryset
                .select_related("passenger")
                .prefetch_related(
                    "tickets",
                    "tickets__flight",
                    "tickets__order",
                    "tickets__flight__airplane",
                    "tickets__flight__crew",
                    "tickets__flight__route__source",
                )
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
