from django.db import transaction
from rest_framework import serializers

from airport.models import Crew, Country, Passenger, Airport, AirplaneType, Airplane, Route, Order, Flight, Ticket


class CountrySerializer(serializers.ModelSerializer):
    airports = serializers.StringRelatedField(many=True, read_only=True, source="airport_name.all")

    class Meta:
        model = Country
        fields = ("name", "population", "net_worth", "airports",)


class CountryAirportSerializer(CountrySerializer):
    class Meta:
        model = Country
        fields = ("name",)


class AirportSerializer(serializers.ModelSerializer):
    country = CountryAirportSerializer(many=False)

    class Meta:
        model = Airport
        fields = ("name", "country", "closest_big_city")


class AirportDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("name",)


class RouteSerializer(serializers.ModelSerializer):
    source = AirportDetailSerializer(many=False)
    destination = AirportDetailSerializer(many=False)

    class Meta:
        model = Route
        fields = ("source", "destination", "distance",)


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("first_name", "last_name", "flights")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("crew", "route", "airplane", "departure_time", "arrival_time")


class CrewFlightSerializer(CrewSerializer):
    class Meta:
        model = Crew
        fields = ("full_name",)


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_seat(
            attrs["seat"],
            attrs["flight"].airplane.seats_in_row,
            attrs["row"],
            attrs["flight"].airplane.rows,
            serializers.ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("seat", "row", "flight")


class TicketFlightSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("seat", "row",)


class FlightDetailSerializer(FlightSerializer):
    crew = CrewFlightSerializer(many=True)
    route = serializers.ReadOnlyField(source="route.__str__")
    airplane = serializers.ReadOnlyField(source="airplane.__str__")
    tickets = TicketFlightSerializer(many=True)

    class Meta:
        model = Flight
        fields = ("crew", "route", "airplane", "departure_time", "arrival_time", "tickets")


class RouteFlightSerializer(RouteSerializer):
    class Meta:
        model = Route
        fields = ("name",)


class FlightListSerializer(FlightSerializer):
    crew = CrewFlightSerializer(many=True)
    route = RouteFlightSerializer(many=False)
    # route = serializers.ReadOnlyField(source="route.__str__")
    airplane = serializers.ReadOnlyField(source="airplane.__str__")
    seats_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = ("crew", "route", "airplane", "departure_time", "arrival_time", "seats_available")


class CrewDetailSerializer(CrewSerializer):
    flights = FlightDetailSerializer(many=True)

    class Meta:
        model = Crew
        fields = ("first_name", "last_name", "flights")


class CrewListSerializer(serializers.ModelSerializer):
    flights = FlightDetailSerializer(many=True)

    class Meta:
        model = Crew
        fields = ("first_name", "last_name", "flights")


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ("first_name", "last_name", "username")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("name",)


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer(many=False)

    class Meta:
        model = Airplane
        fields = ("name", "rows", "seats_in_row", "airplane_type", "capacity")


class AirplaneTicketSerializer(AirplaneSerializer):
    class Meta:
        model = Airplane
        fields = ("name", "airplane_type",)


class FlightTicketSerializer(FlightSerializer):
    route = RouteFlightSerializer(many=False)
    airplane = AirplaneTicketSerializer(many=False)

    class Meta:
        model = Flight
        fields = ("route", "airplane", "departure_time", "arrival_time")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("tickets", "create_at", )

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)
        for ticket_data in tickets_data:
            Ticket.objects.create(order=order, **ticket_data)
        return order


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
