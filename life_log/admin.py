from django.contrib import admin

from models import Event, Query

class EventAdmin(admin.ModelAdmin):
    list_display = ('raw', 'event_dt', 'submitted_dt')

class QueryAdmin(admin.ModelAdmin):
    list_display = ('raw', 'f_raw', 'groupby', 'key', 'count', 'value')

admin.site.register(Event, EventAdmin)
admin.site.register(Query, QueryAdmin)
