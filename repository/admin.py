from django.contrib import admin

from .models import (Department, Exam, Profile, Question, Resource, Subject,
                     User)

admin.site.register(User)
admin.site.register(Department)
admin.site.register(Exam)
admin.site.register(Profile)
admin.site.register(Question)
admin.site.register(Resource)
admin.site.register(Subject)
