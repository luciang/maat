from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

import maat.storer.views
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'maat.storer.views.home', name='home'), #TODO: name='XXX'???
    (r'^assignment/(.*)/$', 'maat.storer.views.assignment_details'),

    # url(r'^maat/', include('maat.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
