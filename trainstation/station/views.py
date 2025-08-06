from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from station.filters import TrainFilter, RouteFilter, JourneyFilter
from station.models import Train, TrainType, Station, Route, Journey, Order
from station.serializers import TrainSerializer, TrainTypeSerializer, StationSerializer, RouteSerializer, \
    JourneySerializer, OrderSerializer, OrderListSerializer, JourneyRetrieveSerializer, JourneyListSerializer, \
    OrderDetailSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related("train_type").all()
    serializer_class = TrainSerializer
    filterset_class = TrainFilter
    filter_backends = [DjangoFilterBackend]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="id", type=int, description="Filter by Train ID (ex. ?id=1,2)"),
            OpenApiParameter(name="name", type=str, description="Filter by Train Name"),
            OpenApiParameter(name="train_type", type=int, description="Filter by Train Type ID"),
            OpenApiParameter(name="train_type_name", type=str, description="Filter by Train Type Name"),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination").all()
    serializer_class = RouteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RouteFilter

    @extend_schema(
        parameters=[
            OpenApiParameter(name="id", type=int, description="Filter by Route ID (ex. ?id=1,2)"),
            OpenApiParameter(name="source", type=str, description="Filter by Route Source Name"),
            OpenApiParameter(name="destination", type=str, description="Filter by Route Destination Name"),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.select_related(
        "route__source",
        "route__destination",
        "train__train_type"
    ).prefetch_related("tickets")
    serializer_class = JourneySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = JourneyFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return JourneyListSerializer
        if self.action == "retrieve":
            return JourneyRetrieveSerializer

        return JourneySerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="id", type=int, description="Filter by Journey ID (ex. ?id=1,2)"),
            OpenApiParameter(name="route", type=str, description="Filter by Route Name"),
            OpenApiParameter(name="train", type=str, description="Filter by Train Name"),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("tickets__journey__train", "tickets__journey__route")
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == "list":
            serializer = OrderListSerializer
        if self.action == "retrieve":
            serializer = OrderDetailSerializer
        return serializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
