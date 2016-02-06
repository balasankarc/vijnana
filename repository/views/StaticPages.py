from django.shortcuts import render
from django.views.generic import View

from shared import current_user


class Home(View):
    """Displays home page"""

    def get(self, request):
        user = current_user(request)
        if user:
            subject_list = []
            if user.status == 'teacher' or user.status == 'hod':
                subject_list = user.teachingsubjects.all()
            else:
                subject_list = user.subscribedsubjects.all()
            return render(request, 'profile.html',
                          {
                              'user': user,
                              'subject_list': subject_list})
        else:
            return render(request, 'home.html')


class About(View):
    """Displays about page"""

    def get(self, request):
        return render(request, 'about.html')
