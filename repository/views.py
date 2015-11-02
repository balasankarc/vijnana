from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt


import os
import random
from datetime import datetime

import bcrypt
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.files.images import get_image_dimensions
from django.db import IntegrityError
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from openpyxl import load_workbook
from PIL import Image

from .forms import (AssignOrRemoveStaffForm, EditProfileForm, NewResourceForm,
                    NewSubjectForm, ProfilePictureCropForm,
                    ProfilePictureUploadForm, QuestionBankUploadForm,
                    QuestionPaperCategoryForm, QuestionPaperGenerateForm,
                    SearchForm, SignInForm, SignUpForm)
from .models import (Department, Exam, Profile, Question, Resource, Subject,
                     User)


def current_user(request):
    """This method returns the current user from session value."""
    if 'user' in request.session:
        return User.objects.get(username=request.session['user'])
    else:
        return None


def is_user_hod(request, subject):
    """This method returns whether the current user is hod of the subject."""
    user = current_user(request)
    if user.status == 'hod' and user.department == subject.department:
        return True
    else:
        return False


class StaticPages:

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
        """Displays home page"""

        def get(self, request):
            return render(request, 'about.html')


class UserActivities:

    class UserSignIn(View):

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

        def get(self, request):
            """Handles user's sign out action"""
            if 'user' in list(request.session.keys()):
                del request.session['user']
                del request.session['usertype']
            return HttpResponseRedirect('/')

    class UserSignUp(View):

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
        """Handles /my_subjects of each user."""

        error = ""
        subject_list = []

        def get(self, request, username):
            user = current_user(request)
            if user:
                if user.status == 'teacher' or user.status == 'hod':
                    self.subject_list = user.teachingsubjects.all()
                else:
                    self.subject_list = user.subscribedsubjects.all()
                if not self.subject_list:
                    self.error = 'You are not subscribed to any subjects'
            else:
                self.error = 'You are not logged in.'
            return render(request, 'my_subjects.html',
                          {
                              'subject_list': self.subject_list,
                              'error': self.error
                          })

    class UploadProfilePicture(View):

        error = ''
        status = 200

        def post(self, request, username):
            """Handles upload of profile picture by user."""
            user = User.objects.get(username=username)
            if not user or user != current_user(request):
                self.error = 'You are not permitted to do this.'
                self.status = 405
                return render(request, 'error.html',
                              {
                                  'error': self.error
                              }, status=self.status)
            else:
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
            if not user or user != current_user(request):
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
        pass


class ResourceActivities:

    class NewResource(View):

        RESOURCE_TYPES = {
            'Presentation': 'presentation',
            'Paper Publication': 'paper_publication',
            'Subject Note': 'subject_note',
            'Project Thesis': 'project_thesis',
            'Seminar Report': 'seminar_report',
            'Previous Question Paper': 'previous_question_paper'
        }
        subject_list = Subject.objects.all()
        error = ""
        template = "newresource.html"

        def get(self, request):
            return render(request, self.template,
                          {
                              'subject_list': self.subject_list,
                              'type_list': self.RESOURCE_TYPES
                          })

        def post(self, request):
            form = NewResourceForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    input_title = form.cleaned_data['title']
                    input_category = form.cleaned_data['category']
                    input_subject = Subject.objects.get(
                        id=form.cleaned_data['subject'])
                    resource_uploader = User.objects.get(
                        username=request.session['user'])
                    input_file = request.FILES['resourcefile']
                    resource = Resource(
                        title=input_title, category=input_category,
                        subject=input_subject, resourcefile=input_file,
                        uploader=resource_uploader)
                    resource.save()
                except Exception as e:
                    self.error = e
                    return render(request, self.template,
                                  {
                                      'error': self.error,
                                      'subject_list': self.subject_list,
                                      'type_list': self.RESOURCE_TYPES
                                  })
            return HttpResponseRedirect('/resource/' + str(resource.id))

    class GetResource(View):

        def get(self, request, resource_id):
            try:
                resource = Resource.objects.get(id=resource_id)
                return render(request, 'resource.html', {'resource': resource})
            except ObjectDoesNotExist:
                return render(request, 'error.html',
                              {
                                  'error': 'The requested resource not found.'
                              }, status=404)

        def post(self, request):
            return render(request, 'error.html',
                          {
                              'error': 'POST method not allowed.'
                          }, status=405)

    class GetResourcesOfType(View):

        RESOURCE_TYPES = {
            'Presentation': 'presentation',
            'Paper Publication': 'paper_publication',
            'Subject Note': 'subject_note',
            'Project Thesis': 'project_thesis',
            'Seminar Report': 'seminar_report',
            'Previous Question Paper': 'previous_question_paper'
        }

        def get(self, request, type_name):
            try:
                type_name = type_name.replace('_', ' ')
                cat = self.RESOURCE_TYPES[type_name]
                resources = Resource.objects.filter(category=cat)
                if resources:
                    return render(request, 'type_resource_list.html',
                                  {
                                      'resource_list': resources,
                                      'type': type_name
                                  })
                else:
                    raise ObjectDoesNotExist
            except ObjectDoesNotExist:
                return render(request, 'error.html',
                              {
                                  'error': 'No resources found.'
                              }, status=404)

    class SearchResource(View):
        """Search for resources having a specific query in their title"""
        template = 'search.html'
        error = ''
        status = ''

        def get(self, request):
            return render(request, self.template)

        def post(self, request):
            try:
                form = SearchForm(request.POST)
                if form.is_valid():
                    query = form.cleaned_data['query']
                    resource_list = Resource.objects.filter(
                        title__contains=query)
                    if resource_list:
                        return render(request, 'search.html',
                                      {
                                          'resource_list': resource_list,
                                          'query': query
                                      })
                    else:
                        raise ObjectDoesNotExist
                else:
                    self.error = 'Something went wrong.'
                    self.status = 500
            except ObjectDoesNotExist:
                self.error = 'Search returned no results.'
                self.status = 404
            return render(request, 'error.html',
                          {
                              'error': self.error
                          }, status=self.status)


class SubjectActivities:
    """Subscribes user to a subject."""

    class NewSubject(View):

        template = 'new_subject.html'
        error = ''
        status = 200

        def get(self, request):
            department_list = Department.objects.all()
            return render(request, self.template,
                          {'department_list': department_list})

        def post(self, request):
            department_list = Department.objects.all()
            try:
                form = NewSubjectForm(request.POST)
                if form.is_valid():
                    input_code = form.cleaned_data['code']
                    input_name = form.cleaned_data['name']
                    input_credit = form.cleaned_data['credit']
                    input_course = form.cleaned_data['course']
                    input_semester = form.cleaned_data['semester']
                    input_department = current_user(request).department.id
                    subject = Subject(code=input_code, name=input_name,
                                      credit=input_credit, course=input_course,
                                      semester=input_semester,
                                      department_id=input_department)
                    subject.save()
                    return HttpResponseRedirect('/subject/' + str(subject.id))
            except IntegrityError:
                self.error = 'Subject Code already exists'
            return render(request, self.template,
                          {
                              'department_list': department_list,
                              'error': self.error},
                          status=self.status)

    class ViewSubject(View):

        error = ''
        status = 200

        def get(self, request, subject_id):
            try:
                subject = Subject.objects.get(id=subject_id)
                resource_list = subject.resource_set.all()
                subscription_status = True
                is_hod = False
                has_staff = False
                is_staff = False
                subject_staff_list = subject.staff.all()
                if subject_staff_list:
                    has_staff = True
                if 'user' in request.session:
                    user = current_user(request)
                    if subject not in user.subscribedsubjects.all():
                        subscription_status = False
                    if user.status == 'hod' and \
                            user.department == subject.department:
                        is_hod = is_user_hod(request, subject)
                    if user in subject.staff.all():
                        is_staff = True
                return render(request, 'subject_resource_list.html',
                              {
                                  'subject': subject,
                                  'resource_list': resource_list,
                                  'subscription_status': subscription_status,
                                  'is_hod': is_hod,
                                  'is_staff': is_staff,
                                  'has_staff': has_staff,
                                  'subject_staff_list': subject_staff_list
                              })
            except ObjectDoesNotExist:
                self.error = 'The subject you requested does not exist.'
                self.status = 404
                return render(request, 'error.html',
                              {
                                  'error': self.error
                              }, status=self.status)

        def post(self, request, subject_id):
            self.error = 'POST Method not supported.'
            self.status = 405
            return render(request, 'error.html',
                          {
                              'error': self.error
                          }, status=self.status)

    class SubscribeUser(View):

        error = ""
        status = 200
        template = "error.html"

        def get(self, request, subject_id):
            try:
                user = current_user(request)
                if user:
                    subject = Subject.objects.get(id=subject_id)
                    subject.students.add(current_user(request))
                    subject.save()
                    return HttpResponseRedirect('/subject/' + subject_id)
                else:
                    self.error = "You are not logged in."
                    self.status = 403
            except ObjectDoesNotExist:
                self.error = "Requested subject not found."
                self.status = 404
            return render(request, self.template,
                          {
                              'error': self.error
                          }, status=self.status)

    class UnsubscribeUser(View):
        """Unsubscribes user from a subject."""

        error = ""
        status = 200
        template = "error.html"

        def get(self, request, subject_id):
            try:
                subject = Subject.objects.get(id=subject_id)
                if 'user' in request.session:
                    user = current_user(request)
                    if user in subject.students.all():
                        subject.students.remove(user)
                        subject.save()
                        return HttpResponseRedirect('/subject/' + subject_id)
                    else:
                        self.error = 'You are not subscribed to this subject.'
                        self.status = 403
                else:
                    self.error = "You are not logged in."
                    self.status = 403
            except ObjectDoesNotExist:
                self.error = 'The subject you requested does not exist.'
            return render(request, self.template,
                          {
                              'error': self.status
                          }, status=self.status)

    class AssignStaff(View):
        """Assigns staff to a subject. Available to HOD of the subject."""

        error = ""
        template = "assign_staff.html"
        status = 200

        def get(self, request, subject_id):
            subject = Subject.objects.get(id=subject_id)
            is_hod = is_user_hod(request, subject)
            staff_list = {}
            for department in Department.objects.all():
                staff_list[department.name] = [x for
                                               x in department.user_set.all()
                                               if x.status == 'teacher' or
                                               x.status == 'hod']
            return render(request, self.template,
                          {
                              'is_hod': is_hod,
                              'staff_list': staff_list,
                              'subject': subject
                          })

        def post(self, request, subject_id):
            subject = Subject.objects.get(id=subject_id)
            is_hod = is_user_hod(request, subject)
            staff_list = {}
            for department in Department.objects.all():
                staff_list[department.name] = [x for
                                               x in department.user_set.all()
                                               if x.status == 'teacher' or
                                               x.status == 'hod']
            try:
                if is_hod:
                    form = AssignOrRemoveStaffForm(request.POST)
                    if form.is_valid():
                        for staff_id in form.cleaned_data['staffselect']:
                            staff = User.objects.get(id=staff_id)
                            subject.staff.add(staff)
                    else:
                        self.error = 'Something went wrong.'
                        self.status = 500
                        raise
                else:
                    self.error = 'You are not an HOD'
                    self.status = 403
            except:
                return render(request, self.template,
                              {
                                  'is_hod': is_hod,
                                  'staff_list': staff_list,
                                  'subject': subject,
                                  'error': self.error
                              }, status=self.status)
            return HttpResponseRedirect('/subject/' + subject_id)

    class RemoveStaff(View):

        error = ""
        template = "remove_staff.html"
        status = 200

        def get(self, request, subject_id):
            subject = Subject.objects.get(id=subject_id)
            is_hod = is_user_hod(request, subject)
            staff_list = subject.staff.all()
            return render(request, self.template,
                          {
                              'is_hod': is_hod,
                              'staff_list': staff_list,
                              'subject': subject
                          })

        def post(self, request, subject_id):
            subject = Subject.objects.get(id=subject_id)
            is_hod = is_user_hod(request, subject)
            staff_list = subject.staff.all()
            try:
                if is_hod:
                    form = AssignOrRemoveStaffForm(request.POST)
                    if form.is_valid():
                        for staff_id in form.cleaned_data['staffselect']:
                            staff = User.objects.get(id=staff_id)
                            subject.staff.remove(staff)
                            subject.save()
                    else:
                        self.error = 'Something went wrong.'
                        self.status = 500
                        raise
                else:
                    self.error = 'You are not an HOD'
                    self.status = 403
            except:
                return render(request, self.template,
                              {
                                  'is_hod': is_hod,
                                  'staff_list': staff_list,
                                  'subject': subject,
                                  'error': self.error
                              }, status=self.status)
            return HttpResponseRedirect('/subject/' + subject_id)


def crop_profilepicture(request, username):
    """Let the user crop the profile picture uploaded."""
    user = User.objects.get(username=username)
    if not user:
        return render(request, 'error.html',
                      {
                          'error': 'The user you requested does not exist.'
                      }, status=404)
    elif user != current_user(request):
        return render(request, 'error.html',
                      {
                          'error': 'You are not permitted to do this.'
                      }, status=404)
    else:
        user = User.objects.get(username=username)
        if request.POST:
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
                    return HttpResponseRedirect('/user/' + user.username)
                else:
                    print("Failure")
                    print(form)
            else:
                return HttpResponseRedirect('/user/' + user.username)
        else:
            return render(request, 'cropprofilepicture.html', {'user': user})


def profile(request, username):
    """Displays profile of a user."""
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


def edit_user(request, username):
    """Let a user edit his/her profile."""
    user = User.objects.get(username=username)
    current_name = user.name or ""
    current_address = user.profile.address or ""
    current_email = user.profile.email or ""
    current_bloodgroup = user.profile.bloodgroup or ""
    if request.POST:
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
        except Exception as e:
            print(e)

    else:
        return render(request, 'edit.html',
                      {'user': user,
                       'current_name': current_name,
                       'current_address': current_address,
                       'current_email': current_email,
                       'current_bloodgroup': current_bloodgroup,
                       })


def read_excel_file(excelfilepath, subject):
    """Read excel file which contains question bank and create question objects
    from it."""
    workbook = load_workbook(filename=excelfilepath)
    for row in workbook.worksheets[0].rows:
        try:
            questiontext = row[1].value
            print("Text", questiontext)
            questionmodule = row[2].value
            questionmark = row[3].value
            question = Question(text=questiontext,
                                module=questionmodule,
                                mark=questionmark
                                )
            question.subject = subject
            question.save()
        except Exception as e:
            print("Error")
            print(e)
            pass


def upload_question_bank(request, subject_id):
    """Let staff of a subject upload a question bank for the subject."""
    subject = Subject.objects.get(id=subject_id)
    if request.POST:
        form = QuestionBankUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                qbfile = request.FILES['qbfile']
                with open('/tmp/qb.xlsx', 'wb') as destination:
                    for chunk in qbfile.chunks():
                        destination.write(chunk)
                read_excel_file('/tmp/qb.xlsx', subject)
                messages.success(request, "Question Bank Uploaded succesfully")
                return HttpResponseRedirect('/subject/' + subject_id)
            except:
                return render(request, 'upload_questionbank.html',
                              {'subject': subject,
                               'error': 'Some problem with the file',
                               'user': current_user(request)})
    else:
        return render(request, 'upload_questionbank.html',
                      {'subject': subject,
                       'user': current_user(request)})


def select_random(itemlist, count):
    """Select n items randomly from a list. (Implements reservoir sampling)"""
    result = []
    N = 0
    for item in itemlist:
        N += 1
        if len(result) < count:
            result.append(item)
        else:
            s = int(random.random() * N)
            if s < count:
                result[s] = item
    return result


def make_pdf(subject, questions, exam, marks, time):
    """Make the pdf of question paper using LaTex."""
    print("Questions")
    print(questions)
    today = datetime.today()
    filename = subject.name.replace(' ', '_') + '_' + \
        str(today.day) + str(today.month) + str(today.year)

    document = Document()

    paragraph = document.add_paragraph()
    paragraph_format = paragraph.paragraph_format
    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph_text = 'Adi Shankara Institute of Engineering and Technology'
    run = paragraph.add_run(paragraph_text)
    run.bold = True
    font = run.font
    font.name = 'Times New Roman'
    font.size = Pt(14)

    paragraph = document.add_paragraph()
    paragraph_format = paragraph.paragraph_format
    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph_text = exam.name
    paragraph.add_run(paragraph_text)

    paragraph = document.add_paragraph()
    paragraph_format = paragraph.paragraph_format
    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph_text = subject.name
    paragraph.add_run(paragraph_text)

    paragraph = document.add_paragraph()
    paragraph_format = paragraph.paragraph_format
    length_of_marks = len(str(marks))
    length_of_time = len(str(time))
    number_of_spaces = 45 - \
        (len('Marks : ') + length_of_marks + len('Time : ') + length_of_time)
    paragraph_text = "Marks : " + \
        str(marks) + " " * (100 - number_of_spaces) + "Time : " + str(time)
    paragraph.add_run(paragraph_text)

#     content = '''
    # \\centering{\\Large{Adi Shankara Institute of Engineering and Technology,
    # Kalady}} \\\\[.5cm]
    # \\centering{\\large{%s}} \\\\[.5cm]
    # \\centering{\\large{%s}} \\\\
    # \\normalsize{Marks: %s \\hfill Time: %s Hrs}\\\\
    # [.5cm]''' % (exam.name, subject.name, marks, time)
    for part in ['Part A', 'Part B', 'Part C']:
        count = 1
        if questions[part]:
            paragraph = document.add_paragraph()
            paragraph_format = paragraph.paragraph_format
            paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph_text = part
            paragraph.add_run(paragraph_text)
            # content = content + '\\centering{%s}\n' % part
            # content = content + '\\begin{enumerate}\n'
            for mark in questions[part]:
                for question in questions[part][mark]:
                    prefix = str(count) + ". "
                    text = prefix + question.text
                    length_of_text = len(text)
                    if length_of_text > 70:
                        pos = text.index(' ', 65)
                        text = text[:pos] + '\n' + \
                            text[pos + 1:]
                        length_of_text = len(text[pos + 1:])
                    paragraph = document.add_paragraph()
                    paragraph_format = paragraph.paragraph_format
                    number_of_spaces = 100 - (length_of_text + len(prefix))
                    paragraph_text = text + " " * \
                        (number_of_spaces) + "\t" + str(question.mark)
                    paragraph.add_run(paragraph_text)
                    count = count + 1
                    # content += '\\item{%s\\hfill%s}\n' %(text, question.mark)
            # content = content + '\\end{enumerate}\n'
    # print content
    document.save('/tmp/' + filename + '.docx')
#     doc = Document(default_filepath='/tmp/' + filename)
    # doc.packages.append(Package('geometry', options=['tmargin=2.5cm',
    # 'lmargin=2.5cm',
    # 'rmargin=3.0cm',
    # 'bmargin=2.0cm']))
    # doc.append(content)
    # doc.generate_pdf()
    qpinfile = open('/tmp/' + filename + '.docx')
    qpfile = File(qpinfile)
    exam.questionpaper.save(filename + '.docx', qpfile)
    return '/uploads/' + exam.questionpaper.url


def create_qp_dataset(subject, exam, totalmarks, time, question_criteria):
    """Populates the dataset needed to generate a question paper. Invokes
    make_pdf() method"""
    questions = {'Part A': {}, 'Part B': {}, 'Part C': {}}
    status = 0
    for trio in question_criteria:
        module = trio[0]
        try:
            mark = int(trio[1])
        except:
            mark = float(trio[1])
        count = int(trio[2])
        questiontotallist = Question.objects.filter(module=module, mark=mark)
        selectedquestions = select_random(questiontotallist, count)
        if subject.course == 'B.Tech':
            if mark >= 10:
                part = 'Part C'
            elif mark >= 4:
                part = 'Part B'
            else:
                part = 'Part A'
        elif subject.course == 'M.Tech':
            if mark >= 10:
                part = 'Part B'
            else:
                part = 'Part A'
        if mark not in questions[part]:
            questions[part][mark] = []
        questions[part][mark] = questions[part][mark] + selectedquestions
    if questions:
        for part in questions:
            for mark in questions[part]:
                for question in questions[part][mark]:
                    exam.question_set.add(question)
                    exam.save()
        status = 1
    path = make_pdf(subject, questions, exam, totalmarks, time)
    return status, path


def generate_question_paper(request, subject_id):
    """Handles interface through which user enters the question paper
    attributes. This method invokes create_qp_dataset() method."""
    error = ''
    subject = Subject.objects.get(id=subject_id)
    QuestionFormSet = formset_factory(QuestionPaperCategoryForm)
    if request.POST:
        print(request.POST)
        QPForm = QuestionPaperGenerateForm(request.POST)
        examname = ''
        totalmarks = ''
        time = ''
        if QPForm.is_valid():
            examname = QPForm.cleaned_data['examname']
            totalmarks = QPForm.cleaned_data['totalmarks']
            time = QPForm.cleaned_data['time']
            exam = Exam(name=examname, totalmarks=totalmarks, time=time,
                        subject_id=subject.id)
            exam.save()
        question_categories_set = QuestionFormSet(request.POST)
        if question_categories_set.is_valid():
            print("\n\n\n\n\n\n Form Data \n\n\n\n\n\n\n\n")
            question_criteria = []
            for form in question_categories_set.forms:
                if form.is_valid():
                    module = form.cleaned_data['module']
                    mark = form.cleaned_data['mark']
                    count = form.cleaned_data['count']
                    question_criteria.append((module, mark, count))
            status, path = create_qp_dataset(subject, exam, totalmarks,
                                             time, question_criteria)
            return HttpResponseRedirect(path)
        else:
            error = 'Choose some questions.'
    else:
        question_categories_set = QuestionFormSet()

    return render(request, 'generatequestionpaper.html',
                  {'subject': subject,
                   'qpformset': question_categories_set,
                   'error': error,
                   'user': current_user(request)})
