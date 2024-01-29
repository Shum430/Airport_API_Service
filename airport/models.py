from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from django.conf import settings


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Country(models.Model):
    name = models.CharField(max_length=255)
    population = models.IntegerField()
    net_worth = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "countries"


class Passenger(AbstractUser):
    class Meta:
        ordering = ("username",)


class Airport(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="airport_name")
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE, related_name="airplanes")

    def __str__(self):
        return f"{self.name} type({self.airplane_type})"

    @property
    def capacity(self):
        return self.rows * self.seats_in_row


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="source_routes")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="destination_routes")
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} - {self.destination}"

    @property
    def name(self):
        return f"{self.source} - {self.destination}"


class Order(models.Model):
    create_at = models.DateTimeField()
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")

    def __str__(self):
        return str(self.passenger) + str(self.create_at)


class Flight(models.Model):
    crew = models.ManyToManyField(Crew, related_name="flights")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{self.route} {self.airplane}"


class Ticket(models.Model):
    seat = models.IntegerField()
    row = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        unique_together = ("seat", "row", "flight")

    def __str__(self):
        return f"{self.flight} {self.seat} {self.row}"

    @staticmethod
    def validate_seat(seat, num_seats, row, num_rows, error_to_raise):
        if not (1 <= seat <= num_seats):
            raise error_to_raise({
                "seat": f"seat must be in  range [1, {num_seats}], not {seat}"
            })
        if not (1 <= row <= num_rows):
            raise error_to_raise({
                "row": f"row must be in  range [1, {num_rows}], not {row}"
            })

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def clean(self):
        Ticket.validate_seat(
            self.seat,
            self.flight.airplane.seats_in_row,
            self.row,
            self.flight.airplane.rows,
            ValidationError
        )
