"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

handler404 = 'main.views.handler404'
handler500 = 'main.views.handler500'

urlpatterns = [
    # HOME
    url(r'^$', 'main.views.index', name='index'),
    url(r'^portfolio/$', 'main.views.portfolio', name='portfolio'),
    url(r'^blog/$', 'main.views.blog', name='blog'),
    url(r'^interests/$', 'main.views.interests', name='interests'),
    url(r'^access_code/$', 'main.views.access_code', name='access_code'),
    url(r'^resume/overview/$', 'main.views.experience_overview', name='experience_overview'),
    url(r'^resume/work/$', 'main.views.experience_work', name='experience_work'),
    url(r'^resume/education/$', 'main.views.experience_education', name='experience_education'),
    url(r'^resume/travel/$', 'main.views.experience_travel', name='experience_travel'),
    
    # STATIC PAGES
    url(r'^(terms|contact|)$', 'main.views.staticpage', name='staticpage'),    
    
    # ADMIN
    url(r'^admin/', include(admin.site.urls)),
    ]
