from django.contrib import admin

from models import AccessCode, Visitor, Message

class AccessCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'created_dt', 'expire_dt')

class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip', 'datetime', 'access_code', 'visits')    
    
class MessageAdmin(admin.ModelAdmin):
    list_display = ('ip', 'email')    
    
admin.site.register(AccessCode, AccessCodeAdmin)
admin.site.register(Visitor, VisitorAdmin)
admin.site.register(Message, MessageAdmin)
