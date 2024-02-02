from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from airport.views import (
    CrewViewSet,
    CountryViewSet,
    UserViewSet,
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
router.register("airports", AirportViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("routes", RouteViewSet)
router.register("orders", OrderViewSet)
router.register("flights", FlightViewSet)

urlpatterns = router.urls + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


app_name = "airport"
