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
                       url(r'^user/(?P<username>[a-zA-Z _0-9]+)/upload_profilepicture(/)?$',
                           UserActivities.UploadProfilePicture.as_view()),
                       url(r'^user/(?P<username>[a-zA-Z _0-9]+)/crop_profilepicture(/)?$',
                           UserActivities.CropProfilePicture.as_view()),
                       url(r'^user/(?P<username>[a-zA-Z _0-9]+)(/)?$',
                           UserActivities.UserProfile.as_view()),
                       url(r'^new_resource/$',
                           ResourceActivities.NewResource.as_view()),
                       url(r'^resource/(?P<resource_id>[0-9]+)/$',
                           ResourceActivities.GetResource.as_view()),
                       url(r'type/(?P<type_name>[a-zA-Z _]+)/$',
                           ResourceActivities.GetResourcesOfType.as_view()),
                       url(r'^search/$',
                           ResourceActivities.SearchResource.as_view()),
                       url(r'subject/(?P<subject_id>[0-9]+)/$',
                           SubjectActivities.ViewSubject.as_view()),
                       url(r'^new_subject/$',
                           SubjectActivities.NewSubject.as_view()),
                       url(r'subject/(?P<subject_id>[0-9]+)/subscribe$',
                           SubjectActivities.SubscribeUser.as_view()),
                       url(r'subject/(?P<subject_id>[0-9]+)/unsubscribe$',
                           SubjectActivities.UnsubscribeUser.as_view()),
                       url(r'subject/(?P<subject_id>[0-9]+)/assign_staff$',
                           SubjectActivities.AssignStaff.as_view()),
                       url(r'subject/(?P<subject_id>[0-9]+)/remove_staff$',
                           SubjectActivities.RemoveStaff.as_view()),
                       url(r'subject/(?P<subject_id>[0-9]+)/upload_questionbank(/)?$',
                           'repository.views.upload_question_bank'),
                       url(r'subject/(?P<subject_id>[0-9]+)/generate_questionpaper(/)?$',
                           'repository.views.generate_question_paper'),
                       url(r'subject/(?P<subject_id>[0-9]+)/unsubscribe_me$',
                           'repository.views.unsubscribe_me'),
                       url(r'^user/(?P<username>[a-zA-Z _0-9]+)/edit(/)?$',
                           'repository.views.edit_user'),
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
