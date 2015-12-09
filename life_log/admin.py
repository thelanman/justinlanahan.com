from django.contrib import admin

from models import Event, Query

class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'raw', 'event_dt', 'submitted_dt')
    filter_horizontal = ('queries',)

    def save_related(self, request, form, *args, **kwargs):
        super(EventAdmin, self).save_related(request, form, *args, **kwargs)
        obj = form.instance
        obj.update_queries()

class QueryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'raw', 'f_raw', 'groupby', 'key', 'count', 'value')
    
    def save_related(self, request, form, *args, **kwargs):
        super(QueryAdmin, self).save_related(request, form, *args, **kwargs)
        obj = form.instance
        obj.update_events()

admin.site.register(Event, EventAdmin)
admin.site.register(Query, QueryAdmin)
