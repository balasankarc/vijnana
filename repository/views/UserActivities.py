import os

import bcrypt
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.images import get_image_dimensions
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from PIL import Image

from repository.forms import (EditProfileForm, ProfilePictureCropForm,
                              ProfilePictureUploadForm, SignInForm, SignUpForm)
from repository.models import Department, Profile, User
from shared import current_user, is_user_current_user


class UserSignIn(View):
    """Handle sign-in action of user"""

    error = ""
    username = ""
    password = ""
    template = "signin.html"

    def get(self, request):
        if 'user' in list(request.session.keys()):
            # If user already logged in, redirect to homepage
            messages.success(request, "You are already signed in.")
            return HttpResponseRedirect('/')
        else:
            return render(request, self.template)

    def post(self, request):
        if 'user' in list(request.session.keys()):
            # If user already logged in, redirect to homepage
            messages.success(request, "You are already signed in.")
            return HttpResponseRedirect('/')
        form = SignInForm(request.POST)
        try:
            if form.is_valid():
                input_username = form.cleaned_data['username']
                input_password_raw = form.cleaned_data['password']
                input_password = input_password_raw.encode('utf-8')
                user = User.objects.get(username=input_username)
                self.username = user.username
                self.password = user.password.encode('utf-8')
                hashed_password = bcrypt.hashpw(input_password,
                                                self.password)
                if hashed_password == self.password:
                    request.session['user'] = self.username
                    request.session['usertype'] = user.status
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
        except:
            self.error = "Missing Field"
            return render(request, self.template,
                          {
                              'error': self.error,
                          })
        return HttpResponseRedirect('/')


class UserSignOut(View):
    """Handle sign-out action of user"""

    def get(self, request):
        if 'user' in list(request.session.keys()):
            del request.session['user']
            del request.session['usertype']
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
                input_name = form.cleaned_data['fullname']
                input_department = form.cleaned_data['department']
                password_hash = bcrypt.hashpw(input_password,
                                              bcrypt.gensalt())
                user = User(username=input_username,
                            password=password_hash,
                            name=input_name,
                            department_id=input_department)
                user.save()
                profile = Profile(user=user)
                profile.save()
                request.session['user'] = input_username
                request.session['usertype'] = user.status
            else:
                raise
        except IntegrityError:
            self.error = "Username already in use"
            return render(request, self.template,
                          {
                              'error': self.error,
                          })
        except:
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
            user = current_user(request)
            if user.status == 'teacher' or user.status == 'hod':
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
            try:
                p = user.profile
            except:
                p = Profile(user_id=user.id)
                p.save()
            form = ProfilePictureUploadForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    image = request.FILES['image']
                    w, h = get_image_dimensions(image)
                    if w < 200 or h < 200 or w > 1000 or h > 1000:
                        error = """Image dimension should be between 500x500
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
        user = User.objects.get(username=username)
        if not is_user_current_user(request, username):
            self.error = 'You are not permitted to do this.'
            self.status = 405
            return render(request, 'error.html',
                          {
                              'error': self.error
                          }, status=self.status)
        else:
            return render(request, 'uploadprofilepicture.html',
                          {'user': user})


class CropProfilePicture(View):
    """Let's user crop an uploaded profile picture."""

    error = ''
    status = 200

    def get(self, request, username):
        user = User.objects.get(username=username)
        if not is_user_current_user(request, username):
            return render(request, 'error.html',
                          {
                              'error': 'You are not permitted to do this.'
                          }, status=404)
        else:
            return render(request, 'cropprofilepicture.html',
                          {'user': user})

    def post(self, request, username):
        user = User.objects.get(username=username)
        if not is_user_current_user(request, username):
            return render(request, 'error.html',
                          {
                              'error': 'You are not permitted to do this.'
                          }, status=404)
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
            subject_list = []
            if user:
                if user.status == 'teacher' or user.status == 'hod':
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
        if not is_user_current_user(request, username):
            return render(request, 'error.html',
                          {
                              'error': 'You are not permitted to do this.'
                          }, status=404)
        else:
            user = User.objects.get(username=username)
            return render(request, 'edit.html', {'user': user})

    def post(self, request, username):
        if not is_user_current_user(request, username):
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
                    name = form.cleaned_data['name'] or ""
                    address = form.cleaned_data['address'] or ""
                    email = form.cleaned_data['email'] or ""
                    bloodgroup = form.cleaned_data['bloodgroup'] or ""
                    user.name = name
                    p = user.profile
                    p.address = address
                    p.email = email
                    p.bloodgroup = bloodgroup
                    p.save()
                    user.save()
                    return HttpResponseRedirect('/user/' + user.username)
            except Exception:
                return HttpResponseRedirect('/user/' + user.usernam)
