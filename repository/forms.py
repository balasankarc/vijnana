from django import forms
from django.contrib.auth.models import User


def get_user_ids():
    try:
        return [(x.id, x.first_name + " " + x.last_name)
                for x in User.objects.all()
                if x.profile.status == 'teacher' or x.profile.status == 'hod']
    except:
        return []


class SignInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class SignUpForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    department = forms.CharField()


class NewResourceForm(forms.Form):
    title = forms.CharField()
    category = forms.CharField()
    subject = forms.CharField()
    resourcefile = forms.FileField()


class SearchForm(forms.Form):
    query = forms.CharField()


class AssignOrRemoveStaffForm(forms.Form):
    user_ids = get_user_ids()
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


class EditProfileForm(forms.Form):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea, required=False)
    email = forms.EmailField(required=False)
    bloodgroup = forms.CharField(required=False)


class QuestionBankUploadForm(forms.Form):
    qbfile = forms.FileField()


class QuestionPaperGenerateForm(forms.Form):
    examname = forms.CharField()
    totalmarks = forms.CharField()
    time = forms.CharField()


class QuestionPaperCategoryForm(forms.Form):
    module = forms.CharField()
    part = forms.CharField()
    level = forms.CharField()
    count = forms.CharField()
