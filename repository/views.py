import bcrypt
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .exceptions import DepartmentNotGivenError
from .forms import SignInForm, SignUpForm
from .models import Department, User


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
                if input_department == 'Department':
                    raise DepartmentNotGivenError
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
            except DepartmentNotGivenError:
                error = error + "Department is mandatory"
    else:
        if 'user' in request.session.keys():
            # If user already logged in, redirect to homepage
            return HttpResponseRedirect('/')
    return render(request, 'signup.html',
                  {'error': error, 'department_list': department_list})
