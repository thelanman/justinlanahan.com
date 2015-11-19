import pickle

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User

import lifelogger.parser
import lifelogger.utils


class Query(models.Model):
    user = models.ForeignKey(User)
    raw = models.TextField()
    key = models.TextField(default='', blank=True)
    f_raw = models.TextField(blank=True, default='len')
    groupby = models.TextField(blank=True, default='')
    q_pickled = models.TextField(blank=True, null=True)
    submitted_dt = models.DateTimeField(auto_now_add=True)
    modified_dt = models.DateTimeField(auto_now=True)
    count = models.IntegerField(default=0, blank=True)
    value = models.TextField(blank=True, default='')

    def clean(self):
        try:
            q = lifelogger.parser.parse_query(self.raw)
        except Exception, e:
            raise ValidationError(str(e))
        #self.q_pickled = pickle.dumps(q)
       
    @classmethod 
    def from_db(cls, db, field_names, values):
        instance = super(Query, cls).from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        #instance.q = pickle.loads(instance._loaded_values['q_pickled'])
        instance.raw_init = instance._loaded_values['raw']
        instance.q = lifelogger.parser.parse_query(instance.raw_init)
        instance.key_init = instance._loaded_values['key']
        instance.f_raw_init = instance._loaded_values['f_raw']
        instance.groupby_init = instance._loaded_values['groupby']
        return instance

    def calculate(self):
        events_data = [e.data for e in self.event_set.objects.all()]
        c, v = lifelogger.utils.calculate(events_data, self.q, self.k, self.f, self.groupby)
        self.count = c
        self.value = str(v)

    def check_events(self):
        for e in Event.objects.filter(user=self.user):
           r =  self.q(e.data)
           if r:
               self.event_set.add(e)

    def update_events(self):
        self.event_set.all().delete()
        self.check_events()

    def save(self):
        if self.pk is not None and (self.raw_init != self.raw or self.key_init != self.key or self.f_raw != self.f_raw_init or self.groupby_init != self.groupby):
            self.update_events()
        if self.pk is None:
            super(Query, self).save()
            self.q = lifelogger.parser.parse_query(self.raw)
            self.check_events()
        super(Query, self).save()
        
    def __unicode__(self):
        return 'Query(%s %s: %s)' % (self.user, self.raw, self.f_raw)

    def __repr__(self):
        return 'Query(%s %s: %s)' % (self.user, self.raw, self.f_raw)


class Event(models.Model):
    user = models.ForeignKey(User)
    queries = models.ManyToManyField(Query, blank=True)
    raw = models.TextField()
    data_pickled = models.TextField(blank=True, null=True)
    submitted_dt = models.DateTimeField(auto_now_add=True)
    event_dt = models.DateTimeField(blank=True, null=True)
    modified_dt = models.DateTimeField(auto_now=True)

    def clean(self):
        data = {}
        try:
            data = lifelogger.parser.parse_event(self.raw, tz='America/New_York')
        except Exception, e:
            raise ValidationError(str(e))
        self.data_pickled = pickle.dumps(data)

    def check_queries(self):
        queries = self.queries.all()
        for q in queries:
            r = q.q(self.data)
            if r:
                q.event_set.add(self)

    def update_queries(self):
        self.queries.all().delete()
        self.check_queries()

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(Event, cls).from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        instance.data = pickle.loads(instance._loaded_values['data_pickled'])
        instance.raw_init = instance._loaded_values['raw']
        instance.event_dt_init = instance._loaded_values['event_dt'] 
        return instance

    def save(self):
        if self.pk is not None and (self.raw_init != self.raw or self.event_dt_init != self.event_dt):
            self.update_queries()
        if self.pk is None:
            super(Event, self).save()
            self.check_queries()
        super(Event, self).save()

    def __unicode__(self):
        return 'Event(%s: %s: %s)' % (self.user, self.event_dt, self.raw)

    def __repr__(self):
        return 'Event(%s: %s: %s)' % (self.user, self.event_dt, self.raw)


