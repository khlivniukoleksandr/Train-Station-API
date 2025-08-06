from django.urls import path, include
from rest_framework.routers import DefaultRouter

from station.views import TrainViewSet, TrainTypeViewSet, StationViewSet, RouteViewSet, JourneyViewSet, OrderViewSet

router = DefaultRouter()
router.register("train-types", TrainTypeViewSet)
router.register("trains", TrainViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("journeys", JourneyViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [
     path("", include(router.urls))
]

app_name = "trainstation"