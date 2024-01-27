from django.contrib import admin
from airport.models import (
    Crew,
    Country,
    Passenger,
    Airport,
    AirplaneType,
    Airplane,
    Route,
    Order,
    Flight,
    Ticket
)

admin.site.register(Crew)
admin.site.register(Country)
admin.site.register(Passenger)
admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Route)
admin.site.register(Order)
admin.site.register(Flight)
admin.site.register(Ticket)

