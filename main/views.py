import datetime

from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from django.utils import timezone

from models import AccessCode, Visitor


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def check_code(request):
    code = request.session.get('access_code', None)
    if code is None:
        return False
    try:
        ac = AccessCode.objects.get(code=code)
        if ac.expire_dt < timezone.now():
            return False
    except:
        return False
    return True
    
class require_code(object): 
    def __init__(self, next='/'):
        self.next = next
        
    def __call__(self, f):
        def do_check(request, *args, **kwargs):
            valid = check_code(request)
            if not valid:
                return redirect('/access_code?next=%s' % self.next)
            return f(request, *args, **kwargs)
        return do_check 
    
# === VIEWS ===    
    
def index(request):
    return render(request, 'page_about_me2.html', {'valid_code': check_code(request)})
    
def portfolio(request):
    return render(request, 'portfolio_3_columns_grid.html', {'valid_code': check_code(request)})

def blog(request):
    return render(request, 'blog_medium_right_sidebar.html', {'valid_code': check_code(request)})
    
    
def interests(request):
    return render(request, 'interests_3_columns_grid.html', {'valid_code': check_code(request)})
    
def access_code(request):
    if request.method == 'POST':
        ac = None
        try:
            ac = AccessCode.objects.get(code=request.POST.get('access_code', ''))
        except:
            return render(request, 'access_code.html', {'error': 'Access code is invalid or expired.'})
        remote_ip = get_client_ip(request)
        ua = request.META['HTTP_USER_AGENT']
        code = request.POST['access_code']
        v = None
        try:
            v = Visitor.objects.get(ip=remote_ip, ua=ua)
        except:
            v = Visitor(ip=remote_ip, ua=ua, access_code=ac)
        v.visits += 1
        v.save()
        request.session['access_code'] = ac.code
        return redirect(request.POST.get('next', '/'))
    return render(request, 'access_code.html', {'valid_code': check_code(request), 'next': request.GET.get('next', '/')})    
    
@require_code('/experience/overview')   
def experience_overview(request):
    return render(request, 'page_profile_me.html', {'valid_code': check_code(request)})    

@require_code('/experience/work')   
def experience_work(request):
    return render(request, 'shortcode_timeline2-work.html', {'valid_code': check_code(request)})

@require_code('/experience/education')     
def experience_education(request):
    return render(request, 'shortcode_timeline2-education.html', {'valid_code': check_code(request)})

@require_code('/experience/travel')     
def experience_travel(request):
    return render(request, 'shortcode_maps_vector.html', {'valid_code': check_code(request)})
    
def staticpage(request, name):
    return render(request, name + '.html', {'valid_code': check_code(request)})    

def handler404(request):
    response = render_to_response('404.html', {'valid_code': check_code(request)}, context_instance=RequestContext(request))
    response.status_code = 404
    return response

def handler500(request):
    response = render_to_response('500.html', {'valid_code': check_code(request)}, context_instance=RequestContext(request))
    response.status_code = 500
    return response