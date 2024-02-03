from django.contrib import admin

from airport.models import (
    Crew,
    Country,
    User,
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
        super().save_model(request, obj, form, change)
        for i in range(1, 6):
            Ticket.objects.create(
                seat=i,
                row=1,
                flight=obj.flights.first(),
                order=obj
            )


admin.site.register(Crew)
admin.site.register(Country)
admin.site.register(User)
admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Route)
admin.site.register(Order, OrderAdmin)
admin.site.register(Flight)
admin.site.register(Ticket)
