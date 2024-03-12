from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Venue, MyClubUsers, Event, Video 


# admin.site.register(Venue)
admin.site.register(MyClubUsers)

admin.site.unregister(Group)
admin.site.register(Video)





@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone')
    ordering = ('name',)
    search_fields = ('name', 'address')
    
    
    
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fields = (('name', 'venue'), 'event_date', 'description', 'manager', 'approved')
    list_display = ('name', 'event_date', 'venue')
    list_filter = ('event_date', 'venue')
    ordering = ('-event_date',)