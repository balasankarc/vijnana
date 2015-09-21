# import hashlib

import bcrypt
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import NewResourceForm, SignInForm, SignUpForm
from .models import Department, Subject, User, Resource


def home(request):
    return render(request, 'home.html')


def user_signin(request):
    error = ""
    username = ""
    if request.POST:
        form = SignInForm(request.POST)
        if form.is_valid():
            input_username = form.cleaned_data['username']
            input_password = form.cleaned_data['password']
            print "Username", input_username
            print "Password", input_password
            try:
                user = User.objects.get(username=input_username)
                username = user.username
                password = user.password
                if bcrypt.hashpw(input_password, password) == password:
                    print "Success"
                    request.session['user'] = username
                    return HttpResponseRedirect('/')
                else:
                    raise ObjectDoesNotExist
            except ObjectDoesNotExist:
                error = "Incorrect username or password"
                print "Exception caught"
    else:
        if 'user' in request.session.keys():
            # If user already logged in, redirect to homepage
            return HttpResponseRedirect('/')
    return render(request, 'signin.html',
                  {'error': error, 'username': username})


def user_signout(request):
    if 'user' in request.session.keys():
        del request.session['user']
    return HttpResponseRedirect('/')


def user_signup(request):
    department_list = Department.objects.all()
    error = ""
    if request.POST:
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                input_username = form.cleaned_data['username']
                input_password = form.cleaned_data['password']
                input_name = form.cleaned_data['fullname']
                input_department = form.cleaned_data['department']
                password_hash = bcrypt.hashpw(input_password, bcrypt.gensalt())
                user = User(username=input_username,
                            password=password_hash,
                            name=input_name,
                            department_id=input_department)
                user.save()
                request.session['user'] = input_username
                return HttpResponseRedirect('/')
            except IntegrityError:
                error = error + "Username already in use"
    else:
        if 'user' in request.session.keys():
            # If user already logged in, redirect to homepage
            return HttpResponseRedirect('/')
    return render(request, 'signup.html',
                  {'error': error, 'department_list': department_list})


def new_resource(request):
    subject_list = Subject.objects.all()
    error = ""
    if request.POST:
        print request.POST
        form = NewResourceForm(request.POST, request.FILES)
        print form
        if form.is_valid():
            try:
                input_title = form.cleaned_data['title']
                input_category = form.cleaned_data['category']
                input_subject = Subject.objects.get(
                    id=form.cleaned_data['subject'])
                input_file = request.FILES['resourcefile']
                resource = Resource(
                    title=input_title, category=input_category,
                    subject=input_subject, resourcefile=input_file)
                resource.save()
                return HttpResponseRedirect('/')
            except Exception, e:
                error = e
                print error
    return render(request, 'newresource.html',
                  {'error': error, 'subject_list': subject_list})
