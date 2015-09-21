from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', 'repository.views.home'),
                       url(r'^sign_in/$', 'repository.views.user_signin'),
                       url(r'^sign_up/$', 'repository.views.user_signup'),
                       url(r'^new_resource/$',
                           'repository.views.new_resource'),
                       url(r'^resource/(?P<resource_id>[0-9]+)/$',
                           'repository.views.get_resource'),
                       url(r'^sign_out/$', 'repository.views.user_signout'),
                       url(r'^uploads/resources/(?P<path>.*)$',
                           'django.views.static.serve',
                           {
                            'document_root': settings.MEDIA_ROOT + 'resources',
                           }
                           )
                       )
