from django.shortcuts import render
from django.views.generic import View

from shared import is_user_hod_or_teacher


class Home(View):
    """Displays home page"""

    def get(self, request):
        if request.user.is_authenticated():
            user = request.user
            subject_list = []
            if is_user_hod_or_teacher(request):
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
