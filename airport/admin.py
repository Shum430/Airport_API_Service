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


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    inlines = [TicketInline]

    def save_model(self, request, obj, form, change):
        # Save the Order model
        super().save_model(request, obj, form, change)

        # Create tickets for the order
        # You can customize this logic based on your requirements
        for i in range(1, 6):  # Assuming you want to create 5 tickets
            Ticket.objects.create(
                seat=i,
                row=1,  # Customize as needed
                flight=obj.flights.first(),  # Assuming you want to link the ticket to the first flight of the order
                order=obj
            )


admin.site.register(Crew)
admin.site.register(Country)
admin.site.register(Passenger)
admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Route)
admin.site.register(Order, OrderAdmin)
admin.site.register(Flight)
admin.site.register(Ticket)

