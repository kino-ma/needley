from django.test import TestCase

from .models import User, Article

fake_avator_url = "https://example.com/icon.png"


class UserModelTests(TestCase):
    def test_lookup_name_with_exist_name(self):
        name = "test-hoge"
        user = User.objects.create(
            name=name, nickname=name, avator=fake_avator_url)
        self.assertEqual(User.lookup_name(name), user)

    def test_lookup_name_with_non_exist_name(self):
        name = "test-hoge"
        non_exist_name = "test-fuga"
        user = User.objects.create(
            name=name, nickname=name, avator=fake_avator_url)
        self.assertEqual(User.lookup_name(non_exist_name), None)
