from django.db import models


class Experience(models.Model):
    title = models.TextField()
    subtitle = models.TextField()
    position = models.TextField(blank=True, default='')
    location = models.TextField()
    tags = models.TextField()
    short_desc = models.TextField(blank=True, default='')
    body = models.TextField()
    img1 = models.TextField(blank=True, default='')
    img2 = models.TextField(blank=True, default='')
    img3 = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    access = models.TextField(blank=True, default='')
    
    def has_access(self, test):
        if test in access:
            return True
        return False
    
    def __unicode__(self):
        return u'Experience(%s: %s)' % (self.title, self.subtitle)
 
    def __repr__(self):
        return 'Experience(%s: %s)' % (self.title, self.subtitle)


class Project(models.Model):
    title = models.TextField()
    subtitle = models.TextField()
    tags = models.TextField()
    body = models.TextField()
    github_url = models.TextField(blank=True, default='')
    blog_url = models.TextField(blank=True, default='')
    img1 = models.TextField(blank=True, default='')
    img2 = models.TextField(blank=True, default='')
    img3 = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    started = models.DateTimeField()
    completed = models.DateTimeField(blank=True, null=True)
    access = models.TextField(blank=True, default='')
    
    def __unicode__(self):
        return u'Project(%s)' % (self.title)
 
    def __repr__(self):
        return 'Project(%s)' % (self.title)


class AccessCode(models.Model):
    code = models.CharField(max_length=16)
    created_dt = models.DateTimeField(auto_now_add=True)
    expire_dt = models.DateTimeField()
    note = models.TextField(blank=True, default='')
    track = models.BooleanField(default=True)
    
    def __unicode__(self):
        return u'AccessCode(%s - %s)' % (self.code, self.expire_dt.strftime('%Y-%m-%d %H:%M'))
 
    def __repr__(self):
        return 'AccessCode(%s - %s)' % (self.code, self.expire_dt.strftime('%Y-%m-%d %H:%M'))

        
class Visitor(models.Model):
    ip = models.CharField(max_length=15)
    ua = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    visits = models.IntegerField(default=0)
    note = models.TextField(blank=True, default='')
    
    def __unicode__(self):
        return u'Visitor(%s #:%s)' % (self.ip, self.visits)
 
    def __repr__(self):
        return 'Visitor(%s #:%s)' % (self.ip, self.visits)

class VisitorHasAccessCode(models.Model):
    visitor = models.ForeignKey(Visitor)
    access_code = models.ForeignKey(AccessCode)
    visits = models.IntegerField(default=0)
    
    def __unicode__(self):
        return u'Has(%s -> %s)' % (self.visitor, self.access_code)
 
    def __repr__(self):
        return 'Has(%s -> %s)' % (self.visitor, self.access_code)
    
class PageVisit(models.Model):
    visitor = models.ForeignKey(Visitor)
    page_url = models.TextField()
    access_code = models.ForeignKey(AccessCode)
    anchor = models.TextField(blank=True, default='')
    datetime = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return u'PageVisit(%s - %s : %s - %s)' % (self.visitor, self.page_url, self.anchor, self.datetime.strftime('%Y-%m-%d %H:%M'))
 
    def __repr__(self):
        return 'PageVisit(%s - %s : %s - %s)' % (self.visitor, self.page_url, self.anchor, self.datetime.strftime('%Y-%m-%d %H:%M'))
        
      
class Message(models.Model):
    ip = models.CharField(max_length=15)
    ua = models.TextField()
    name = models.CharField(blank=False, max_length=50)
    email = models.EmailField(blank=False, max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=False)
    
    def __unicode__(self):
        return u'Message(%s - %s)' % (self.created.strftime('%Y-%m-%d %H:%M'), self.ip)
 
    def __repr__(self):
        return 'Message(%s - %s)' % (self.created.strftime('%Y-%m-%d %H:%M'), self.ip)
 
 
 