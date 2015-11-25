import pickle
import logging

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete, post_delete

import lifelogger.parser
import lifelogger.utils


logger = logging.getLogger(__name__)


class Query(models.Model):
    user = models.ForeignKey(User)
    name = models.TextField(blank=False, null=False)
    raw = models.TextField()
    key = models.TextField(default='', blank=True)
    f_raw = models.TextField(blank=True, default='len')
    groupby = models.TextField(blank=True, default='')
    submitted_dt = models.DateTimeField(auto_now_add=True)
    modified_dt = models.DateTimeField(auto_now=True)
    count = models.IntegerField(default=0, blank=True)
    value = models.TextField(blank=True, default='')

    def clean(self):
        try:
            self.q = lifelogger.parser.parse_query(self.raw)
        except Exception, e:
            raise ValidationError(str(e))
       
    @classmethod 
    def from_db(cls, db, field_names, values):
        instance = super(Query, cls).from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        instance.raw_init = instance._loaded_values['raw']
        instance.q = lifelogger.parser.parse_query(instance.raw_init)
        instance.key_init = instance._loaded_values['key']
        instance.f_raw_init = instance._loaded_values['f_raw']
        instance.groupby_init = instance._loaded_values['groupby']
        return instance

    def calculate(self, event_data=None):
        events_data = [e.data for e in self.event_set.all()] if event_data is None else event_data
        c, v = lifelogger.utils.calculate(events_data, self.q, self.key, self.f_raw, self.groupby)
        self.count = c
        self.value = str(v)

    def check_events(self):
        event_data = []
        for e in Event.objects.filter(user=self.user):
            r =  self.q(e.data)
            if r:
                self.event_set.add(e)
                event_data += [e.data]
        self.calculate(event_data)

    def update_events(self):
        self.event_set.clear()
        self.check_events()

    def save(self, *args, **kwargs):
        created = self.pk is None
        self.full_clean()
        if not created and (self.raw_init != self.raw or self.key_init != self.key or self.f_raw != self.f_raw_init or self.groupby_init != self.groupby):
            logger.debug('NOT CREATED %s %s %s' % (self.raw_init != self.raw, self.key_init != self.key, self.f_raw != self.f_raw_init))
            self.update_events()
            logger.debug('UPDATE EVENTS %s %s' % (self.count, self.value))
            super(Query, self).save(*args, **kwargs)
            logger.debug('UPDATE EVENTS %s %s' % (self.count, self.value))
        elif created:
            self.raw_init = self.raw
            self.key_init = self.key
            self.f_raw_init = self.f_raw
            self.groupby_init = self.groupby
            super(Query, self).save(*args, **kwargs)
            logger.debug('CR UPDATE EVENTS %s %s' % (self.count, self.value))
            self.check_events()
            logger.debug('Cr UPDATE EVENTS %s %s' % (self.count, self.value))
            super(Query, self).save(*args, **kwargs)
            logger.debug('Cr UPDATE EVENTS %s %s' % (self.count, self.value))
        

    def __unicode__(self):
        return 'Query(%s:%s "%s" %s(%s) = %s)' % (self.user, self.name, self.raw, self.f_raw, self.key, self.value)

    def __repr__(self):
        return 'Query(%s:%s "%s" %s(%s) = %s)' % (self.user, self.name, self.raw, self.f_raw, self.key, self.value)

        
class Event(models.Model):
    user = models.ForeignKey(User)
    queries = models.ManyToManyField(Query, blank=True)
    raw = models.TextField()
    data_pickled = models.TextField(blank=True, null=True)
    submitted_dt = models.DateTimeField(auto_now_add=True)
    event_dt = models.DateTimeField(blank=True, null=True)
    modified_dt = models.DateTimeField(auto_now=True)

    def clean(self):
        try:
            dt = timezone.now() if '@' not in self.raw and self.event_dt is None else None
            self.data = lifelogger.parser.parse_event(self.raw, start_tz='America/New_York', end_tz='America/New_York', dt=dt)
        except Exception, e:
            raise ValidationError(str(e))
        self.event_dt = self.data.get('datetime', self.event_dt if self.event_dt is not None else lifelogger.parser.convert_tz(timezone.now(), 'UTC', 'America/New_York'))
        self.raw = lifelogger.utils.data_to_raw(self.data)
        self.data_pickled = pickle.dumps(self.data)


    def check_queries(self):
        queries = Query.objects.filter(user=self.user)
        for q in queries:
            r = q.q(self.data)
            if r:
                self.queries.add(q)
                q.calculate()
                q.save()

    def update_queries(self):
        self.queries.clear()
        self.check_queries()

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(Event, cls).from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        data_pickled = instance._loaded_values.get('data_pickled', None)
        instance.data = pickle.loads(data_pickled) if data_pickled is not None else {}
        instance.raw_init = instance._loaded_values['raw']
        instance.event_dt = lifelogger.parser.convert_tz(instance._loaded_values['event_dt'], start_tz='UTC', end_tz='America/New_York')
        instance.data['year'] = instance.event_dt.year
        instance.data['month'] = instance.event_dt.month
        instance.data['day'] = instance.event_dt.day
        instance.data['weekday'] = instance.event_dt.weekday()
        instance._loaded_values['event_dt'] = instance.event_dt
        instance.event_dt_init = instance._loaded_values['event_dt'] 
        return instance

    def save(self, *args, **kwargs):
        created = self.pk is None
        self.full_clean()
        if self.pk is not None and (self.raw_init != self.raw or self.event_dt_init != self.event_dt):
            self.update_queries()
        if self.pk is None:
            self.raw_init = self.raw
            self.event_dt_init = self.event_dt
        super(Event, self).save(*args, **kwargs)
        if created:
            self.check_queries()

    def __unicode__(self):
        return 'Event(%s: %s: %s)' % (self.user, self.event_dt, self.raw)

    def __repr__(self):
        return 'Event(%s: %s: %s)' % (self.user, self.event_dt, self.raw)


def event_pre_delete(sender, *args, **kwargs):
    instance = kwargs['instance']
    queries = instance.queries.all()
    for q in queries:
        instance.queries.remove(q)
        q.calculate()
        q.save()

pre_delete.connect(event_pre_delete, sender=Event)
