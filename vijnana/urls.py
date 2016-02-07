from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve

from repository.views import (ResourceActivities, StaticPages,
                              SubjectActivities, UserActivities)

urlpatterns = [
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
    url(r'^user/(?P<username>[a-zA-Z _0-9]+)/edit(/)?$',
        UserActivities.EditUser.as_view()),
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
        SubjectActivities.UploadQuestionBank.as_view()),
    url(r'subject/(?P<subject_id>[0-9]+)/generate_questionpaper(/)?$',
        SubjectActivities.GenerateQuestionPaper.as_view()),
    url(r'subject/(?P<subject_id>[0-9]+)/questions(/)?$',
        SubjectActivities.ViewQuestions.as_view()),
    url(r'subject/(?P<subject_id>[0-9]+)/questionpapers(/)?$',
        SubjectActivities.ViewQuestionpapers.as_view()),
    url(r'subject/(?P<subject_id>[0-9]+)/questionpaper/(?P<exam_id>[0-9]+)(/)?$',
        SubjectActivities.ViewAQuestionpaper.as_view()),
    url(r'^subjects$',
        SubjectActivities.ViewSubjects.as_view()),
    url(r'^uploads/resources/(?P<path>.*)$',
        serve,
        {
            'document_root': settings.MEDIA_ROOT + 'resources',
        }
        ),
    url(r'^uploads/profile_pictures/(?P<path>.*)$',
        serve,
        {
            'document_root': settings.MEDIA_ROOT +
            'profile_pictures',
        }
        ),
    url(r'^uploads/questionpapers/(?P<path>.*)$',
        serve,
        {
            'document_root': settings.MEDIA_ROOT +
            'questionpapers',
        }
        )
]
