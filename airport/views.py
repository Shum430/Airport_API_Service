from django.db.models import Count, F
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from airport.models import (
    Crew,
    Country,
    User,
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
    UserSerializer,
    AirportSerializer,
    AirplaneSerializer,
    RouteSerializer,
    OrderSerializer,
    FlightSerializer,
    AirplaneTypeSerializer,
    CrewDetailSerializer,
    CrewListSerializer,
    FlightDetailSerializer,
    FlightListSerializer,
    OrderListSerializer,
    AirplaneImageSerializer,
)
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly


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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
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


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAuthenticated,)

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
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        if source and destination:
            queryset = queryset.filter(
                source__name__icontains=source,
                destination__name__icontains=destination
            )

        if self.action == "list":
            (
                queryset
                .select_related("source", "destination")
                .prefetch_related(
                    "source__country",
                    "source__destination_routes",
                )
            )

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(name='source', description='Filter by source city', required=False, type=str),
            OpenApiParameter(name='destination', description='Filter by destination city', required=False, type=str),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, IsAuthenticated)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = (
                queryset
                .select_related("user")
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
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, IsAuthenticated)

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
