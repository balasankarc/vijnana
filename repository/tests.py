from django.test import TestCase
from .models import User
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
