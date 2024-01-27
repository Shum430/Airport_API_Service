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
    TicketViewSet
)

router = routers.DefaultRouter()
router.register("crews", CrewViewSet)
router.register("countries", CountryViewSet)
router.register("passengers", PassengerViewSet)
router.register("airplanes", AirportViewSet)
router.register("airports", AirplaneViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("routes", RouteViewSet)
router.register("orders", OrderViewSet)
router.register("tickets", TicketViewSet)
router.register("fights", FlightViewSet)

urlpatterns = router.urls


app_name = "airport"
