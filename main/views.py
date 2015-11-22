from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.utils import timezone
from django.contrib.auth.models import User

from models import AccessCode, Visitor, Message, Project, Experience, VisitorHasAccessCode
from helpers import *        


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def ip(request):
    return HttpResponse(get_client_ip(request))        

def index(request):
    projects = Project.objects.all()
    return render(request, 'page_about_me2.html', {'valid_code': check_code(request), 'projects': projects})
    
    
def portfolio(request):
    projects = Project.objects.all()
    return render(request, 'portfolio_3_columns_grid.html', {'valid_code': check_code(request), 'projects': projects})

    
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
        v = Visitor.objects.get_or_create(ip=remote_ip, ua=ua)[0]
        v.visits += 1
        v.save()
        v_has_ac = VisitorHasAccessCode.objects.get_or_create(visitor=v, access_code=ac)[0]
        v_has_ac.visits += 1
        v_has_ac.save()
        request.session['access_code'] = ac.code
        next = request.POST.get('next', '/')
        next = '/' if next == '' else next
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
    return render(request, 'page_contact2.html', {'valid_code': check_code(request)})
    
    
@require_code   
def resume_overview(request):
    experiences = Experience.objects.all().order_by('-end')
    return render(request, 'private/page_profile_me.html', {'valid_code': check_code(request), 'experiences': experiences})    

@require_code   
def resume_work(request):
    work = Experience.objects.all().order_by('-end')
    return render(request, 'shortcode_timeline2-work.html', {'valid_code': check_code(request), 'work': work})

@require_code  
def resume_education(request):
    education = Experience.objects.all().order_by('-end')
    return render(request, 'shortcode_timeline2-education.html', {'valid_code': check_code(request), 'education': education})

@require_code     
def travel(request):
    return render(request, 'shortcode_maps_vector.html', {'valid_code': check_code(request)})
 
def project(request, id):
    p = None
    try:
        p = Project.objects.get(id=int(id))
    except:
        return handler404(request)
    return render(request, 'project1.html', {'project': p})
        
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

