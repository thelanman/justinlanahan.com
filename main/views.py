import datetime

from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.utils import timezone

from models import AccessCode, Visitor, Message


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
            return render(request, 'access_code.html', {'valid_code': check_code(request), 'error': 'Access code is invalid or expired.'})
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
    
def contact(request):
    if request.method == 'POST':
        ip = get_client_ip(request)
        ua = request.META['HTTP_USER_AGENT']
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')
        msg = None
        try:
            print 'TRYING MESSAGE', name, email, message
            msg = Message(ip=ip, ua=ua, name=name, email=email, message=message)
            msg.save()
            print 'MESSAGE SAVED'
        except Exception, e:
            print 'ERROR', str(e)
            return render(request, 'page_contact2.html', {'valid_code': check_code(request), 'error': 'invalid form'})
        return render(request, 'page_contact2.html', {'valid_code': check_code(request), 'success': 'Thanks for the message'})
    print 'MESSAGE get'
    return render(request, 'page_contact2.html', {'valid_code': check_code(request)})
    
    
@require_code('/resume/overview')   
def experience_overview(request):
    return render(request, 'private/page_profile_me.html', {'valid_code': check_code(request)})    

@require_code('/resume/work')   
def experience_work(request):
    return render(request, 'private/shortcode_timeline2-work.html', {'valid_code': check_code(request)})

@require_code('/resume/education')     
def experience_education(request):
    return render(request, 'private/shortcode_timeline2-education.html', {'valid_code': check_code(request)})

@require_code('/resume/travel')     
def experience_travel(request):
    return render(request, 'shortcode_maps_vector.html', {'valid_code': check_code(request)})
    
def staticpage(request, name):
    if name == 'robots.txt':
        return HttpResponse('User-agent: *\nDisallow: /resume', content_type='text/plain')
    return render(request, name + '.html', {'valid_code': check_code(request)})    

def handler404(request):
    response = render_to_response('404.html', {'valid_code': check_code(request)}, context_instance=RequestContext(request))
    response.status_code = 404
    return response

def handler500(request):
    response = render_to_response('500.html', {'valid_code': check_code(request)}, context_instance=RequestContext(request))
    response.status_code = 500
    return response