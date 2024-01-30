from rest_framework import routers

from airport.views import (
    CrewViewSet,
    CountryViewSet,
    PassengerViewSet,
    AirplaneViewSet,
    AirportViewSet,
    AirplaneTypeViewSet,
    RouteViewSet,
    OrderViewSet,
    FlightViewSet,
)

router = routers.DefaultRouter()
router.register("crews", CrewViewSet)
router.register("countries", CountryViewSet)
router.register("passengers", PassengerViewSet)
router.register("airports", AirportViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("routes", RouteViewSet)
router.register("orders", OrderViewSet)
router.register("flights", FlightViewSet)

urlpatterns = router.urls


app_name = "airport"
