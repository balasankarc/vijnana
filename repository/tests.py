from django.db import IntegrityError
from django.test import TestCase

from .models import Subject, User
import bcrypt


class UserTests(TestCase):

    @classmethod
    def setUp(inp):
        password = bcrypt.hashpw('testuser0', bcrypt.gensalt())
        first_user = User(
            username='testuser0', password=password, department_id=1)
        first_user.save()

    def test_user_department_not_null(self):
        first_user = User(username='testuser1')
        with self.assertRaises(IntegrityError):
            first_user.save()

    def test_user_signup_missing_field(self):
        response = self.client.post("/sign_up/",
                                    {'username': 'testuser3',
                                     'fullname': 'Test User 3',
                                     'department': '1'})
        self.assertTemplateUsed(response, 'signup.html')

    def test_user_signup_and_signout_successfull(self):
        response = self.client.post("/sign_up/",
                                    {'username': 'testuser3',
                                     'password': 'testuser3',
                                     'fullname': 'Test User 3',
                                     'department': '1'})
        self.assertRedirects(response, '/')
        self.assertEqual(self.client.session['user'], 'testuser3')
        user = User.objects.get(id=2)
        self.assertEqual(user.status, 'student')
        response = self.client.get('/sign_out/')
        self.assertRedirects(response, '/')
        self.assertNotIn('user', self.client.session)

    def test_signin_success(self):
        response2 = self.client.post("/sign_in/",
                                     {'username': 'testuser0',
                                      'password': 'testuser0'})
        self.assertRedirects(response2, '/')
        self.assertEqual(self.client.session['user'], 'testuser0')

    def test_incorrect_signin(self):
        response2 = self.client.post("/sign_in/",
                                     {'username': 'testuser0',
                                      'password': 'testuser1'})
        self.assertTemplateUsed(response2, 'signin.html')

    def test_already_signedin(self):
        response2 = self.client.post("/sign_in/",
                                     {'username': 'testuser0',
                                      'password': 'testuser0'})
        response2 = self.client.get("/sign_in/")
        self.assertRedirects(response2, '/')

    def test_signup_already_signed_in(self):
        response2 = self.client.post("/sign_in/",
                                     {'username': 'testuser0',
                                      'password': 'testuser0'})
        response2 = self.client.get("/sign_up/")
        self.assertRedirects(response2, '/')


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
