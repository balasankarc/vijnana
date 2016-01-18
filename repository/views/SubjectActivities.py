from django.views.generic import View
from django.contrib import messages
from django.forms.formsets import formset_factory
from shared import current_user, is_user_hod

from django.shortcuts import render
from django.http import HttpResponseRedirect

from repository.forms import (NewSubjectForm, AssignOrRemoveStaffForm,
                              QuestionBankUploadForm,
                              QuestionPaperCategoryForm,
                              QuestionPaperGenerateForm)

from repository.models import User, Department, Subject, Question, Exam
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from openpyxl import load_workbook
import random
from datetime import datetime

from odf.opendocument import OpenDocumentText
from django.core.files import File
from odf.style import (Style, TextProperties, ParagraphProperties,
                       ListLevelProperties, TabStop, TabStops)
from odf.text import H, P, List, ListItem, ListStyle, ListLevelStyleNumber
from odf import teletype


class NewSubject(View):
    """Let's a new subject to be created"""

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
    """Display details of a subject"""

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
    """Let's a user subscribe to a subject"""

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
    """Let's a user unsubscribe to a subject"""

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
    """Removes staff from a subject. Available to HOD of the subject."""

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


class UploadQuestionBank(View):
    """Upload a subject's question bank"""

    def read_excel_file(self, excelfilepath, subject):
        """Read excel file which contains question bank and create question objects
        from it."""
        workbook = load_workbook(filename=excelfilepath)
        for row in workbook.worksheets[0].rows:
            try:
                questiontext = row[1].value
                print "Question Text: ", questiontext
                questionmodule = row[2].value
                print "Question Module: ", questionmodule
                questionpart = row[4].value
                print "Question Part: ", questionpart
                questionco = row[3].value
                print "Question CO: ", questionco
                questionlevel = row[5].value
                print "Question Level: ", questionlevel
                question = Question(text=questiontext,
                                    module=questionmodule,
                                    part=questionpart,
                                    co=questionco,
                                    level=questionlevel
                                    )
                question.subject = subject
                question.save()
                print questiontext, questionmodule, questionpart, \
                    questionco, questionlevel
            except Exception as e:
                print("Error")
                print(e)
                pass

    def get(self, request, subject_id):
        subject = Subject.objects.get(id=subject_id)
        return render(request, 'upload_questionbank.html',
                      {'subject': subject,
                       'user': current_user(request)})

    def post(self, request, subject_id):
        subject = Subject.objects.get(id=subject_id)
        form = QuestionBankUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                qbfile = request.FILES['qbfile']
                with open('/tmp/qb.xlsx', 'wb') as destination:
                    for chunk in qbfile.chunks():
                        destination.write(chunk)
                self.read_excel_file('/tmp/qb.xlsx', subject)
                messages.success(request, "Uploaded succesfully")
                return HttpResponseRedirect('/subject/' + subject_id)
            except:
                return render(request, 'upload_questionbank.html',
                              {'subject': subject,
                               'error': 'Some problem with the file',
                               'user': current_user(request)})
        else:
            return render(request, 'upload_questionbank.html',
                          {'subject': subject,
                           'error': 'Some problem with the file',
                           'user': current_user(request)})


class GenerateQuestionPaper(View):
    """Generate subject's question paper"""

    def get(self, request, subject_id):
        error = ''
        subject = Subject.objects.get(id=subject_id)
        QuestionFormSet = formset_factory(QuestionPaperCategoryForm)
        question_categories_set = QuestionFormSet()
        return render(request, 'generatequestionpaper.html',
                      {'subject': subject,
                       'qpformset': question_categories_set,
                       'error': error,
                       'user': current_user(request)})

    def select_random(self, itemlist, count):
        """Select n items randomly from a list. (Reservoir sampling)"""
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

    def make_document(self, subject, questions, exam, marks, time):
        """Create a document from the generated question set"""
        today = datetime.today()
        filename = subject.name.replace(' ', '_') + '_' + \
            str(today.day) + str(today.month) + str(today.year)
        textdoc = OpenDocumentText()
        s = textdoc.styles
        h1style = Style(name="Heading 1", family="paragraph")
        h1style.addElement(ParagraphProperties(
            attributes={'textalign': "center"}))
        h1style.addElement(TextProperties(
            attributes={'fontsize': "18pt", 'fontweight': "bold"}))
        h2style = Style(name="Heading 2", family="paragraph")
        h2style.addElement(ParagraphProperties(
            attributes={'textalign': "center"}))
        h2style.addElement(TextProperties(
            attributes={'fontsize': "15pt", 'fontweight': "bold"}))
        h3style = Style(name="Heading 3", family="paragraph")
        h3style.addElement(ParagraphProperties(
            attributes={'textalign': "center"}))
        h3style.addElement(TextProperties(
            attributes={'fontsize': "13pt", 'fontweight': "bold"}))
        s.addElement(h1style)
        s.addElement(h2style)
        s.addElement(h3style)

        # Adding tab-stop at 16cm  for questions
        tabstops_style = TabStops()
        tabstop_style = TabStop(position="16cm")
        tabstops_style.addElement(tabstop_style)
        questionpar = ParagraphProperties()
        questionpar.addElement(tabstops_style)
        questionstyle = Style(name="Question", family="paragraph")
        questionstyle.addElement(questionpar)
        s.addElement(questionstyle)

        # Adding tab-stop at 14cm for Time-Marks
        tabstops_style1 = TabStops()
        tabstop_style1 = TabStop(position="15cm")
        tabstops_style1.addElement(tabstop_style1)
        markpar = ParagraphProperties()
        markpar.addElement(tabstops_style1)
        markstyle = Style(name="Mark", family="paragraph")
        markstyle.addElement(markpar)
        s.addElement(markstyle)

        # Adding Numbered List
        listhier = ListStyle(name="MyList")
        level = 1
        b = ListLevelStyleNumber(
            level=str(level))
        b.setAttribute('numsuffix', ".")
        listhier.addElement(b)
        b.addElement(ListLevelProperties(
            minlabelwidth="%fcm" % (level - .2)))

        s.addElement(listhier)
        collegename = H(outlinelevel=1, stylename=h1style,
                        text="Adi Shankara Institute of Engineering \
                                and Technology")
        textdoc.text.addElement(collegename)
        subjectname = H(outlinelevel=1, stylename=h2style, text=subject)
        textdoc.text.addElement(subjectname)
        p = P(stylename=markstyle)
        teletype.addTextToElement(
            p, u"Time: " + time + "Hours\tMarks: " + marks + "\n")
        textdoc.text.addElement(p)
        for part in ['Part A', 'Part B', 'Part C']:
            if questions[part]:
                print part
                partname = H(outlinelevel=1, stylename=h3style, text=part)
                textdoc.text.addElement(partname)
                partlist = List(stylename=listhier)
                textdoc.text.addElement(partlist)
                for question in questions[part]:
                    oldtext = question.text
                    remainingtext = oldtext
                    stripedtext = ""
                    newtext = ""
                    while True:
                        if len(remainingtext) > 80:
                            try:
                                pos = remainingtext.index(' ', 75)
                            except:
                                pos = len(remainingtext) - \
                                    remainingtext[::-1].index(' ')
                            stripedtext = remainingtext[:pos] + "\n"
                            remainingtext = remainingtext[pos + 1:]
                            newtext += stripedtext
                        else:
                            newtext += remainingtext
                            break
                    # tabs = "\t"  # * (count / 10)
                    # newtext += tabs + question.mark
                    elem = ListItem()
                    p = P(stylename=questionstyle)
                    teletype.addTextToElement(p, newtext)
                    elem.addElement(p)
                    partlist.addElement(elem)
        textdoc.save("/tmp/" + filename + ".odt")
        qpinfile = open('/tmp/' + filename + '.odt')
        qpfile = File(qpinfile)
        exam.questionpaper.save(filename + '.odt', qpfile)
        return '/uploads/' + exam.questionpaper.url

    def create_qp_dataset(self, subject, exam, totalmarks, time, criteria):
        """Populates the dataset needed to generate a question paper. Invokes
        make_document() method"""
        questions = {'Part A': [], 'Part B': [], 'Part C': []}
        status = 0
        for trio in criteria:
            module = trio[0]
            part = trio[1]
            level = trio[2]
            count = int(trio[3])
            questiontotallist = Question.objects.filter(
                module=module, part=part, level=level)
            part = "Part " + part
            selectedquestions = self.select_random(
                questiontotallist, count)
            questions[part] = questions[part] + selectedquestions
        if questions:
            for part in questions:
                for question in questions[part]:
                    exam.question_set.add(question)
                    exam.save()
            status = 1
        path = self.make_document(subject, questions, exam, totalmarks, time)
        return status, path

    def post(self, request, subject_id):
        error = ''
        subject = Subject.objects.get(id=subject_id)
        QuestionFormSet = formset_factory(QuestionPaperCategoryForm)
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
        print question_categories_set
        if question_categories_set.is_valid():
            print("\n\n\n\n\n\n Form Data \n\n\n\n\n\n\n\n")
            question_criteria = []
            for form in question_categories_set.forms:
                if form.is_valid():
                    module = form.cleaned_data['module']
                    part = form.cleaned_data['part']
                    level = form.cleaned_data['level']
                    count = form.cleaned_data['count']
                    question_criteria.append((module, part, level, count))
            status, path = self.create_qp_dataset(subject, exam,
                                                  totalmarks, time,
                                                  question_criteria)
            return HttpResponseRedirect(path)
        else:
            error = 'Choose some questions.'
            return render(request, 'generatequestionpaper.html',
                          {'subject': subject,
                           'qpformset': question_categories_set,
                           'error': error,
                           'user': current_user(request)})
