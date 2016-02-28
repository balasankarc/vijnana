from django.db import IntegrityError
from django.test import TestCase

from .models import Subject, Profile
from django.contrib.auth.models import User


class UserTests(TestCase):

    @classmethod
    def setUp(inp):
        first_user = User.objects.create(username='testuser0')
        first_user.set_password('testuser0')
        first_user.save()
        p = Profile.objects.create(user=first_user, department_id=1)
        p.save()

    def test_user_signup_missing_field(self):
        response = self.client.post("/sign_up/",
                                    {'username': 'testuser3',
                                     'fullname': 'Test User 3',
                                     'department': '1'})
        self.assertTemplateUsed(response, 'signup.html')

    def test_user_signup_and_signout_successfull(self):
        self.client.post("/sign_up/",
                         {'username': 'testuser3',
                          'password': 'testuser3',
                          'first_name': 'Test',
                          'last_name': 'User 3',
                          'department': '1'})
        user = User.objects.last()
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)
        self.assertEqual(user.profile.status, 'student')
        self.client.get('/sign_out/')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_signin_form(self):
        response2 = self.client.get("/sign_in/")
        self.assertTemplateUsed(response2, 'signin.html')

    def test_signup_form(self):
        response2 = self.client.get("/sign_up/")
        self.assertTemplateUsed(response2, 'signup.html')

    def test_signin_success(self):
        response2 = self.client.post("/sign_in/",
                                     {'username': 'testuser0',
                                      'password': 'testuser0'})
        self.assertRedirects(response2, '/')
        self.assertIn('_auth_user_id', self.client.session)

    def test_incorrect_signin(self):
        response2 = self.client.post("/sign_in/",
                                     {'username': 'testuser0',
                                      'password': 'testuser1'})
        self.assertTemplateUsed(response2, 'signin.html')

    def test_incomplete_signin_form(self):
        response2 = self.client.post("/sign_in/",
                                     {'username': '',
                                      'password': 'testuser1'})
        self.assertTemplateUsed(response2, 'signin.html')

    def test_already_signedin(self):
        response2 = self.client.post("/sign_in/",
                                     {'username': 'testuser0',
                                      'password': 'testuser0'})
        response2 = self.client.get("/sign_in/")
        self.assertRedirects(response2, '/')
        response2 = self.client.post("/sign_in/",
                                     {'username': 'testuser0',
                                      'password': 'testuser0'})
        self.assertRedirects(response2, '/')

    def test_signup_already_signed_in(self):
        response2 = self.client.post("/sign_in/",
                                     {'username': 'testuser0',
                                      'password': 'testuser0'})
        response2 = self.client.get("/sign_up/")
        self.assertRedirects(response2, '/')
        response2 = self.client.post("/sign_up/")
        self.assertRedirects(response2, '/')

    def test_username_uniqueness(self):
        response2 = self.client.post("/sign_up/",
                                     {'username': 'testuser4',
                                      'password': 'testuser4',
                                      'first_name': 'Test',
                                      'last_name': 'User 4',
                                      'department': '1'})


class SubjectTests(TestCase):

    def test_subject_required_not_null(self):
        first_subject = Subject(code='subject1')
        with self.assertRaises(IntegrityError):
            first_subject.save()

    def test_subject_unique_code(self):
        first_subject = Subject(code='testsubject2', department_id=1)
        first_subject.save()
        with self.assertRaises(IntegrityError):
            second_subject = Subject(code='testsubject2', department_id=1)
            second_subject.save()

    def test_subject_exists(self):
        first_subject = Subject(code='testsubject2', department_id=1)
        first_subject.save()
        response = self.client.get('/subject/1/')
        self.assertEqual(response.status_code, 200)

    def test_subject_not_exists(self):
        response = self.client.get('/subject/1/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'error.html')


class LinkTests(TestCase):

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
