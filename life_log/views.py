import json
import math

from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.template import RequestContext
from django.utils import timezone
from django.views.generic import ListView, View
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

from models import Event, Query


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


def is_valid(n, t):
    try:
        n = t(n) if t is not type(None) else n
        if t is type(None) and n not in ['None', None]:
            return False
        return True
    except:
        return False

class APIView(LoginRequiredMixin, View):
    model = None
    fields = ('id', )
    param_fields = [('page', 1), ('size', 100)]

    def get(self, request):
        self.validate_input(request) 
        data = {'data': []}
        objects = self.get_queryset(request)
        data['total'] = objects.count()
        self.set_paging(request, data['total'])
        data['count'] = min(data['total'], self.size)
        if data['total'] == 0:        
            return HttpResponse(json.dumps(data), content_type='application/json')
        objects = objects[(self.page - 1) * self.size: self.page * self.size]
        data['data'] = self.dictify_objects(objects, self.fields)                
        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

    def validate_input(self, request):
        for f, default in self.param_fields:
            temp = request.GET.get(f, default)
            if not is_valid(temp, type(default)):
                raise Http404("Parameter must be number")
            self.__setattr__(f, type(default)(temp) if default is not None else None)                

    def set_paging(self, request, total):
        self.size = min(self.size, 100)
        pages = math.ceil(total / float(self.size))
        if self.page > pages and total > 0:
            raise Http404("Requested page does not exists")

    def dictify_objects(self, objs, fields=None):
        obj_dicts = []
        for obj in objs:
            temp = {}
            for f in fields:
                temp[f] = obj.__getattribute__(f)
            obj_dicts += [temp]
        return obj_dicts

    def get_queryset(self, request):
        return self.model.objects.filter(user=request.user)


class EventView(APIView):
    model = Event
    fields = ('id', 'raw', 'event_dt', 'submitted_dt')
    param_fields = [('page', 1), ('size', 100), ('query_id', None)]

    def get_queryset(self, request):
        if self.query_id is None:
            return super(EventView, self).get_queryset(request)
        query = get_object_or_404(Query, user=request.user, pk=self.query_id)
        return query.event_set.all()
 
class QueryView(APIView):
    model = Query
    fields = ('id', 'raw', 'f_raw', 'key', 'groupby', 'count', 'value')
 


