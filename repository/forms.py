from django import forms
from .models import User


class SignInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class SignUpForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
    fullname = forms.CharField()
    department = forms.CharField()


class NewResourceForm(forms.Form):
    title = forms.CharField()
    category = forms.CharField()
    subject = forms.CharField()
    resourcefile = forms.FileField()


class SearchForm(forms.Form):
    query = forms.CharField()


class AssignOrRemoveStaffForm(forms.Form):
    user_ids = [(x.id, x.name)
                for x in User.objects.all()
                if x.status == 'teacher' or x.status == 'hod']
    staffselect = forms.MultipleChoiceField(choices=user_ids)


class NewSubjectForm(forms.Form):
    code = forms.CharField()
    name = forms.CharField()
    credit = forms.CharField()
    course = forms.CharField()
    semester = forms.CharField()


class ProfilePictureUploadForm(forms.Form):
    image = forms.ImageField()


class ProfilePictureCropForm(forms.Form):
    x1 = forms.CharField()
    y1 = forms.CharField()
    x2 = forms.CharField()
    y2 = forms.CharField()
    w = forms.CharField()
    h = forms.CharField()
