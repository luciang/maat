from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

import maat.storer.views
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    (r'^$', 'maat.storer.views.home'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', { 'template_name' : 'storer/templates/login.html' }),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^assignment/(?P<ass_name>[^/]+)/$', 'maat.storer.views.assignment_form'),
    (r'^assignment/(?P<ass_name>[^/]+)/(?P<username>[^/]+)/$', 'maat.storer.views.current_submission'),
    (r'^assignment/(?P<ass_name>[^/]+)/(?P<username>[^/]+)/(?P<subm_id>[^/]+)/$', 'maat.storer.views.submission'),

    # url(r'^maat/', include('maat.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
