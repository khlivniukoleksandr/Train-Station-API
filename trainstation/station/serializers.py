from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from station.models import TrainType, Train, Station, Route, Journey, Ticket, Order


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):
    train_type = serializers.PrimaryKeyRelatedField(
        queryset=TrainType.objects.all(), write_only=True
    )
    train_type_detail = TrainTypeSerializer(source='train_type', read_only=True)

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type", "train_type_detail")


    def create(self, validated_data):
        train_type = validated_data.pop("train_type")
        train = Train.objects.create(train_type=train_type, **validated_data)
        return train


class StationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        queryset=Station.objects.all(),
        slug_field="name",
    )
    destination = serializers.SlugRelatedField(
        queryset=Station.objects.all(),
        slug_field="name",
    )


    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time")


class JourneyListSerializer(serializers.ModelSerializer):
    train = serializers.SlugRelatedField(
        queryset=Train.objects.all(),
        slug_field="name",
    )
    route_write = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.all(),
        write_only=True,
    )
    route = serializers.SerializerMethodField(read_only=True)
    tickets_available = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Journey
        fields = ("id", "route_write", "route", "train", "departure_time", "arrival_time", "tickets_available")

    def create(self, validated_data):
        route = validated_data.pop("route_write")
        journey = Journey.objects.create(route=route, **validated_data)
        return journey

    def get_route(self, obj):
        return f"{obj.route.source.name} - {obj.route.destination.name}"

    def get_tickets_available(self, obj):
        total_seats = obj.train.cargo_num * obj.train.places_in_cargo
        taken_seats = obj.tickets.count()
        return total_seats - taken_seats


class JourneyRetrieveSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    train = TrainSerializer(read_only=True)
    taken_seats = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "taken_seats")

    def get_taken_seats(self, obj):
        return [
            {"cargo": ticket.cargo, "seat": ticket.seat}
            for ticket in obj.tickets.all()
        ]


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["cargo"],
            attrs["seat"],
            attrs["journey"].train,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")

class TicketListSerializer(TicketSerializer):
    journey = JourneySerializer(read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("cargo", "seat")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")


    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)




