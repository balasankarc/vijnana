from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', 'repository.views.home'),
                       url(r'^sign_in/$', 'repository.views.user_signin'),
                       url(r'^sign_up/$', 'repository.views.user_signup'),
                       url(r'^new_subject/$',
                           'repository.views.new_subject'),
                       url(r'^new_resource/$',
                           'repository.views.new_resource'),
                       url(r'^resource/(?P<resource_id>[0-9]+)/$',
                           'repository.views.get_resource'),
                       url(r'^sign_out/$', 'repository.views.user_signout'),
                       url(r'type/(?P<type_name>[a-zA-Z _]+)/$',
                           'repository.views.type_resource_list'),
                       url(r'subject/(?P<subject_id>[0-9]+)/$',
                           'repository.views.view_subject'),
                       url(r'subject/(?P<subject_id>[0-9]+)/subscribe_me$',
                           'repository.views.subscribe_me'),
                       url(r'subject/(?P<subject_id>[0-9]+)/unsubscribe_me$',
                           'repository.views.unsubscribe_me'),
                       url(r'subject/(?P<subject_id>[0-9]+)/remove_staff$',
                           'repository.views.remove_staff'),
                       url(r'subject/(?P<subject_id>[0-9]+)/assign_staff$',
                           'repository.views.assign_staff'),
                       url(r'^search/$', 'repository.views.search'),
                       url(r'^my_subjects/$', 'repository.views.my_subjects'),
                       url(r'^user/(?P<username>[a-zA-Z _0-9]+)(/)?$',
                           'repository.views.profile'),
                       url(r'^user/(?P<username>[a-zA-Z _0-9]+)/upload_profilepicture(/)?$',
                           'repository.views.upload_profilepicture'),
                       url(r'^user/(?P<username>[a-zA-Z _0-9]+)/crop_profilepicture(/)?$',
                           'repository.views.crop_profilepicture'),
                       url(r'^uploads/resources/(?P<path>.*)$',
                           'django.views.static.serve',
                           {
                            'document_root': settings.MEDIA_ROOT + 'resources',
                           }
                           ),
                       url(r'^uploads/profile_pictures/(?P<path>.*)$',
                           'django.views.static.serve',
                           {
                            'document_root': settings.MEDIA_ROOT + 'profile_pictures',
                           }
                           )
                       )
