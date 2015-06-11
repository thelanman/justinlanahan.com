from django.db import models


class AccessCode(models.Model):
    code = models.CharField(max_length=16)
    created_dt = models.DateTimeField(auto_now_add=True)
    expire_dt = models.DateTimeField()
    
    def __unicode__(self):
        return u'AccessCode(%s - %s)' % (self.code, self.expire_dt.strftime('%Y-%m-%d %H:%M'))
 
    def __repr__(self):
        return 'AccessCode(%s - %s)' % (self.code, self.expire_dt.strftime('%Y-%m-%d %H:%M'))

class Visitor(models.Model):
    ip = models.CharField(max_length=15)
    ua = models.TextField()
    access_code = models.ForeignKey(AccessCode)
    datetime = models.DateTimeField(auto_now_add=True)
    visits = models.IntegerField(default=0)
    
    def __unicode__(self):
        return u'Visitor(%s - %s - %s - %s)' % (self.ip, self.access_code.code, self.datetime.strftime('%Y-%m-%d %H:%M'), self.visits)
 
    def __repr__(self):
        return 'Visitor(%s - %s - %s - %s)' % (self.ip, self.access_code.code, self.datetime.strftime('%Y-%m-%d %H:%M'), self.visits)
 
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
 