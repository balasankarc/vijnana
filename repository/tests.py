from django.test import TestCase
from .models import User, Subject
from django.db import IntegrityError


class UserTests(TestCase):
    def test_user_department_not_null(self):
        first_user = User(username='testuser1')
        with self.assertRaises(IntegrityError):
            first_user.save()

    def test_user_uniqueness(self):
        first_user = User(username='testuser2', department_id=1)
        first_user.save()
        with self.assertRaises(IntegrityError):
            second_user = User(username='testuser2', department_id=1)
            second_user.save()


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


class LinkTests(TestCase):
    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_subject_exists(self):
        first_subject = Subject(code='testsubject2', department_id=1)
        first_subject.save()
        response = self.client.get('/subject/1/')
        self.assertEqual(response.status_code, 200)

    def test_subject_not_exists(self):
        response = self.client.get('/subject/1/')
        self.assertEqual(response.status_code, 404)
