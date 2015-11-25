import json
import math
import datetime

from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.template import RequestContext
from django.utils import timezone
from django.views.generic import ListView, View
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder

from models import Event, Query

import logging
logger = logging.getLogger(__name__)


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
    default_param_fields = [('page', 1), ('size', 10000), ('id', -1), ('action', 'get')]
    param_fields = []
    response = HttpResponse(content_type='application/json')

    def delete(self, request):
        try:
            obj = self.model.objects.get(user=request.user, pk=self.id)
            obj.delete()
            return self.respond({'status': 'success'})
        except:
            return self.respond({'status': 'error', 'message': 'unexpected error'})
            
    def edit(self, request):
        pass 

    def respond(self, data, content_type='application/json', encoder=DjangoJSONEncoder, status_code=200):
        response = HttpResponse(json.dumps(data, cls=encoder), content_type=content_type)
        response.status_code = status_code
        return response

    def get_list(self, request):
        data = {'data': []}
        objects = self.get_queryset(request)
        data['total'] = objects.count()
        self.set_paging(request, data['total'])
        data['page'] = self.page
        data['size'] = self.size
        data['next'] = self.page + 1 if self.page != self.pages else None
        data['prev'] = self.page - 1 if self.page != 1 else None
        data['count'] = min(data['total'], self.size)
        if data['total'] == 0:        
            return HttpResponse(json.dumps(data), content_type='application/json')
        objects = objects[(self.page - 1) * self.size: self.page * self.size]
        data['data'] = self.dictify_objects(objects, self.fields)                
        return self.respond(data)

    def get_obj(self, request):
        obj = get_object_or_404(self.model, pk=self.id, user=request.user)
        data = self.dictify_objects([obj], self.fields)
        return self.respond(data[0])

    def get(self, request):
        self.validate_input(request, 'GET')
        if self.id == -1:
            return self.get_list(request)
        return self.get_obj(request)

    def post(self, request):
        self.validate_input(request, 'POST')
        if self.action == 'delete':
            return self.delete(request)
        params = dict([(n, request.POST[n]) for n in self.model._meta.get_all_field_names() if n in request.POST])
        params['user'] = request.user
        try:
            m = self.model(**params)
            m.save()
            return self.respond({'status': 'success', 'data':self.dictify_objects([m], self.fields)})
        except ValidationError, e:
            return self.respond({'status':'error', 'message': str(e), 'data': []}, status_code=400)

    def validate_input(self, request, method='GET'):
        for f, default in self.default_param_fields + self.param_fields:
            temp = request.GET.get(f, default) if method == 'GET' else request.POST.get(f, default)
            if not is_valid(temp, type(default)):
                return self.respond({'status':'error', 'message': 'Parameter must be number'}, status_code=400)
            self.__setattr__(f, type(default)(temp) if default is not None else None)                

    def set_paging(self, request, total):
        self.size = min(self.size, 10000)
        self.pages = math.ceil(total / float(self.size))
        if self.page > self.pages and total > 0:
            return self.respond({'status':'error', 'message':'Requested page does not exists'}, status_code=404)

    def dictify_objects(self, objs, fields=None):
        obj_dicts = []
        for obj in objs:
            temp = {}
            for f in fields:
                temp[f] = obj.__getattribute__(f)
                if type(temp[f]) == datetime.datetime:
                    temp[f] = temp[f].strftime('%Y-%m-%dT%H:%M')
            obj_dicts += [temp]
        return obj_dicts

    def get_queryset(self, request):
        return self.model.objects.filter(user=request.user)


class EventView(APIView):
    model = Event
    fields = ('id', 'raw', 'event_dt', 'submitted_dt')
    param_fields = [('query_id', -1)]

    def get_queryset(self, request):
        if self.query_id == -1:
            return super(EventView, self).get_queryset(request)
        query = get_object_or_404(Query, user=request.user, pk=self.query_id)
        return query.event_set.all()


class QueryView(APIView):
    model = Query
    fields = ('id', 'name', 'raw', 'f_raw', 'key', 'groupby', 'count', 'value')
 

# NORMAL VIEWS
@login_required()
def events(request):
    query_id = request.GET.get('query_id', None)
    return render(request, 'events.html', {'query_id': query_id})


@login_required()
def queries(request):
    return render(request, 'queries.html', {})
