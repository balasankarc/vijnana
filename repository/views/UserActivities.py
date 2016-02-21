import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.images import get_image_dimensions
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from PIL import Image

from repository.forms import (EditProfileForm, ProfilePictureCropForm,
                              ProfilePictureUploadForm, SignInForm, SignUpForm)
from repository.models import Department, Profile
from shared import is_user_current_user, is_user_hod_or_teacher


class UserSignIn(View):
    """Handle sign-in action of user"""

    error = ""
    username = ""
    password = ""
    template = "signin.html"

    def get(self, request):
        if request.user.is_authenticated():
            # If user already logged in, redirect to homepage
            messages.success(request, "You are already signed in.")
            return HttpResponseRedirect('/')
        else:
            return render(request, self.template)

    def post(self, request):
        if request.user.is_authenticated():
            messages.success(request, "You are already signed in.")
            return HttpResponseRedirect('/')
        form = SignInForm(request.POST)
        try:
            if form.is_valid():
                input_username = form.cleaned_data['username']
                input_password_raw = form.cleaned_data['password']
                input_password = input_password_raw.encode('utf-8')
                user = authenticate(username=input_username,
                                    password=input_password)
                print user
                if user is not None:
                    if user.is_active:
                        request.session['user'] = self.username
                        login(request, user)
                else:
                    raise ObjectDoesNotExist
            else:
                raise
        except ObjectDoesNotExist:
            self.error = "Incorrect username or password"
            return render(request, self.template,
                          {
                              'error': self.error,
                              'username': self.username
                          })
        except Exception, e:
            print e
            self.error = "Missing Field"
            return render(request, self.template,
                          {
                              'error': self.error,
                          })
        return HttpResponseRedirect('/')


class UserSignOut(View):
    """Handle sign-out action of user"""

    def get(self, request):
        if request.user and request.user.is_authenticated():
            logout(request)
        return HttpResponseRedirect('/')


class UserSignUp(View):
    """Handle sign-up action of user"""

    department_list = Department.objects.all()
    error = ""
    template = 'signup.html'

    def get(self, request):
        if 'user' in list(request.session.keys()):
            # If user already logged in, redirect to homepage
            messages.success(request, "You are already signed in.")
            return HttpResponseRedirect('/')
        else:
            return render(request, self.template,
                          {'department_list': self.department_list})

    def post(self, request):
        if 'user' in list(request.session.keys()):
            # If user already logged in, redirect to homepage
            messages.success(request, "You are already signed in.")
            return HttpResponseRedirect('/')

        form = SignUpForm(request.POST)
        try:
            if form.is_valid():
                input_username = form.cleaned_data['username']
                input_password_raw = form.cleaned_data['password']
                input_password = input_password_raw.encode('utf-8')
                input_first_name = form.cleaned_data['first_name']
                input_last_name = form.cleaned_data['last_name']
                input_department = form.cleaned_data['department']
                user = User.objects.create(username=input_username,
                                           first_name=input_first_name,
                                           last_name=input_last_name)
                user.set_password(input_password)
                user.save()
                profile = Profile(user=user, department_id=input_department)
                profile.status = 'student'
                profile.save()
                user = authenticate(username=input_username,
                                    password=input_password)
                login(request, user)
            else:
                raise
        except IntegrityError:
            self.error = "Username already in use"
            return render(request, self.template,
                          {
                              'error': self.error,
                          })
        except Exception, e:
            print e
            self.error = "Missing field."
            return render(request, self.template,
                          {
                              'error': self.error,
                          })
        return HttpResponseRedirect('/')


class UserSubjects(View):
    """Displays subjects associated to user."""

    error = ""
    subject_list = []
    status = 200

    def get(self, request, username):
        if is_user_current_user(request, username):
            user = request.user
            if is_user_hod_or_teacher(request):
                self.subject_list = user.teachingsubjects.all()
            else:
                self.subject_list = user.subscribedsubjects.all()
            if not self.subject_list:
                self.error = 'You are not subscribed to any subjects'
                self.status = 404
        else:
            self.error = 'You are not logged in or not allowed to access \
                    this page.'
            self.status = 404
        return render(request, 'my_subjects.html',
                      {
                          'subject_list': self.subject_list,
                          'error': self.error
                      }, status=self.status)


class UploadProfilePicture(View):
    """Let's user upload a profile picture."""

    error = ''
    status = 200

    def post(self, request, username):
        """Handles upload of profile picture by user."""
        if not is_user_current_user(request, username):
            self.error = 'You are not permitted to do this.'
            self.status = 405
            return render(request, 'error.html',
                          {
                              'error': self.error
                          }, status=self.status)
        else:
            user = User.objects.get(username=username)
            p = user.profile
            form = ProfilePictureUploadForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    image = request.FILES['image']
                    w, h = get_image_dimensions(image)
                    if w < 200 or h < 200 or w > 1000 or h > 1000:
                        error = """Image dimension should be between 200x200
                        and 1000x1000"""
                        raise
                    if p.picture:
                        os.remove(p.picture.path)
                    p.picture = image
                    p.save()
                    print(p.picture.path)
                    returnpath = '/user/' + \
                        user.username + '/crop_profilepicture'
                    return HttpResponseRedirect(returnpath)
                except:
                    return render(request, 'uploadprofilepicture.html',
                                  {'user': user, 'error': error})
            else:
                return render(request, 'uploadprofilepicture.html',
                              {'user': user})

    def get(self, request, username):
        if not request.user.is_authenticated() or \
                not is_user_current_user(request, username):
            self.error = 'You are not permitted to do this.'
            self.status = 405
            return render(request, 'error.html',
                          {
                              'error': self.error
                          }, status=self.status)
        else:
            return render(request, 'uploadprofilepicture.html',
                          {'user': request.user})


class CropProfilePicture(View):
    """Let's user crop an uploaded profile picture."""

    error = ''
    status = 200

    def get(self, request, username):
        if not request.user.is_authenticated() or \
                not is_user_current_user(request, username):
            return render(request, 'error.html',
                          {
                              'error': 'You are not permitted to do this.'
                          }, status=404)
        else:
            return render(request, 'cropprofilepicture.html',
                          {'user': request.user})

    def post(self, request, username):
        if not request.user.is_authenticated() or \
                not is_user_current_user(request, username):
            return render(request, 'error.html',
                          {
                              'error': 'You are not permitted to do this.'
                          }, status=404)
        user = request.user
        if user.profile.picture:
            form = ProfilePictureCropForm(request.POST)
            if form.is_valid():
                x1 = int(float(form.cleaned_data['x1']))
                y1 = int(float(form.cleaned_data['y1']))
                x2 = int(float(form.cleaned_data['x2']))
                y2 = int(float(form.cleaned_data['y2']))
                image = Image.open(user.profile.picture.path)
                cropped_image = image.crop((x1, y1, x2, y2))
                cropped_image.save(user.profile.picture.path)
                return HttpResponseRedirect('/user/' +
                                            user.username)
        return HttpResponseRedirect('/user/' + user.username)


class UserProfile(View):
    """Displays profile of a user."""

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            print user.profile.status
            subject_list = []
            if user:
                if is_user_hod_or_teacher(request):
                    subject_list = user.teachingsubjects.all()
                else:
                    subject_list = user.subscribedsubjects.all()
            return render(request, 'profile.html',
                          {
                              'user': user,
                              'subject_list': subject_list})
        except Exception as e:
            print(e)
            return render(request, 'error.html',
                          {
                              'error': 'The requested user not found.'
                          }, status=404)


class EditUser(View):
    """Lets a user edit his/her profile."""

    def get(self, request, username):
        if request.user.username != username:
            return render(request, 'error.html',
                          {
                              'error': 'You are not permitted to do this.'
                          }, status=404)
        else:
            user = User.objects.get(username=username)
            return render(request, 'edit.html', {'user': user})

    def post(self, request, username):
        if request.user.username != username:
            return render(request, 'error.html',
                          {
                              'error': 'You are not permitted to do this.'
                          }, status=404)
        else:

            user = User.objects.get(username=username)
            form = EditProfileForm(request.POST)
            try:
                if form.is_valid():
                    print("Here")
                    print(form)
                    first_name = form.cleaned_data['first_name'] or ""
                    last_name = form.cleaned_data['last_name'] or ""
                    address = form.cleaned_data['address'] or ""
                    email = form.cleaned_data['email'] or ""
                    bloodgroup = form.cleaned_data['bloodgroup'] or ""
                    user.first_name = first_name
                    user.last_name = last_name
                    p = user.profile
                    p.address = address
                    user.email = email
                    p.bloodgroup = bloodgroup
                    p.save()
                    user.save()
                    return HttpResponseRedirect('/user/' + user.username)
                else:
                    print form
            except Exception:
                return HttpResponseRedirect('/user/' + user.username)
