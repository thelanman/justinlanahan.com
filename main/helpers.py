from django.shortcuts import redirect
from django.utils import timezone

from models import AccessCode, Visitor, PageVisit, VisitorHasAccessCode


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

    
def do_track(request, ac):
    if not ac.track:
        return
    ip = get_client_ip(request)
    ua = request.META['HTTP_USER_AGENT']
    v = Visitor.objects.get_or_create(ip=ip, ua=ua)
    if v[1]:
        v[0].visits += 1
        v[0].save()
        v_has_ac = VisitorHasAccessCode.objects.get_or_create(visitor=v[0], access_code=ac)[0]
        v_has_ac.visits += 1
        v_has_ac.save()
    pv = PageVisit(visitor=v[0], access_code=ac, page_url=request.path, anchor=request.GET.get('anc', ''))
    pv.save()
    

def check_code(request):
    code = request.session.get('access_code', None)
    if code is None:
        return False
    try:
        ac = AccessCode.objects.get(code=code)
        do_track(request, ac)
        if ac.expire_dt < timezone.now():
            return False
    except:
        return False
    return True
   
   
def require_code(f):
    def do_check(request):
        valid = check_code(request)
        if not valid:
            return redirect('/access_code?next=%s' % request.path)
        return f(request)
    return do_check 