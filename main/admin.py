from django.contrib import admin

from models import AccessCode, Visitor, Message, Project, Experience, PageVisit, VisitorHasAccessCode

class AccessCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'created_dt', 'expire_dt')

class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip', 'datetime', 'visits')    

class VisitorHasAccessCodeAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'access_code')      
    
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'datetime', 'page_url', 'anchor')
    
class MessageAdmin(admin.ModelAdmin):
    list_display = ('ip', 'email', 'created')    
   
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle')
   
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'position', 'access')
   
admin.site.register(AccessCode, AccessCodeAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Experience, ExperienceAdmin)
admin.site.register(Visitor, VisitorAdmin)
admin.site.register(VisitorHasAccessCode, VisitorHasAccessCodeAdmin)
admin.site.register(PageVisit, PageVisitAdmin)
admin.site.register(Message, MessageAdmin)
