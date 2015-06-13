from django.shortcuts import redirect
from django.utils import timezone

from models import AccessCode, Visitor, PageVisit


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

    
def do_track(request, code):
    ip = get_client_ip(request)
    ua = request.META['HTTP_USER_AGENT']
    v = None
    try:
        v = Visitor.objects.get(ip=ip, ua=ua, access_code=code.id)
    except Exception, e:
        return
    pv = PageVisit(visitor=v, page_url=request.path, anchor=request.GET.get('anc', ''))
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