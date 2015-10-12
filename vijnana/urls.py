from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib import admin

from repository.views import (ResourceActivities, StaticPages,
                              SubjectActivities, UserActivities)

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', StaticPages.Home.as_view()),
                       url(r'^about/$', StaticPages.About.as_view()),
                       url(r'^sign_up/$',
                           UserActivities.UserSignUp.as_view()),
                       url(r'^sign_in/$',
                           UserActivities.UserSignIn.as_view()),
                       url(r'^sign_out/$',
                           UserActivities.UserSignOut.as_view()),
                       url(r'^user/(?P<username>[a-zA-Z _0-9]+)/subjects(/)?$',
                           UserActivities.UserSubjects.as_view()),
                       url(r'^new_subject/$',
                           'repository.views.new_subject'),
                       url(r'^new_resource/$',
                           ResourceActivities.NewResource.as_view()),
                       url(r'^resource/(?P<resource_id>[0-9]+)/$',
                           ResourceActivities.GetResource.as_view()),
                       url(r'type/(?P<type_name>[a-zA-Z _]+)/$',
                           ResourceActivities.GetResourcesOfType.as_view()),
                       url(r'^search/$',
                           ResourceActivities.SearchResource.as_view()),
                       url(r'subject/(?P<subject_id>[0-9]+)/$',
                           'repository.views.view_subject'),
                       url(r'subject/(?P<subject_id>[0-9]+)/subscribe$',
                           SubjectActivities.SubscribeUser.as_view()),
                       url(r'subject/(?P<subject_id>[0-9]+)/unsubscribe$',
                           SubjectActivities.UnsubscribeUser.as_view()),
                       url(r'subject/(?P<subject_id>[0-9]+)/upload_questionbank(/)?$',
                           'repository.views.upload_question_bank'),
                       url(r'subject/(?P<subject_id>[0-9]+)/generate_questionpaper(/)?$',
                           'repository.views.generate_question_paper'),
                       url(r'subject/(?P<subject_id>[0-9]+)/unsubscribe_me$',
                           'repository.views.unsubscribe_me'),
                       url(r'subject/(?P<subject_id>[0-9]+)/remove_staff$',
                           'repository.views.remove_staff'),
                       url(r'subject/(?P<subject_id>[0-9]+)/assign_staff$',
                           'repository.views.assign_staff'),
                       url(r'^user/(?P<username>[a-zA-Z _0-9]+)/edit(/)?$',
                           'repository.views.edit_user'),
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
                               'document_root': settings.MEDIA_ROOT +
                               'profile_pictures',
                           }
                           ),
                       url(r'^uploads/questionpapers/(?P<path>.*)$',
                           'django.views.static.serve',
                           {
                               'document_root': settings.MEDIA_ROOT +
                               'questionpapers',
                           }
                           )
                       )
