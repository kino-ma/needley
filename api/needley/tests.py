from django.test import TestCase
from graphene.test import Client

from .models import User, Article
from .schema import schema

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


def create_user_mutation(name, nickname, avator=None):
    return f'''
        mutation {{
            createUser(input: {{
                userName:"{name}",
                userNickname:"{nickname}",
                { 'userAvator:' + avator if avator else "" }
            }}) {{
                user {{
                    name
                    nickname
                    avator
                }}
            }}
        }}
        '''


class CreateUserTests(TestCase):
    def test_create_user(self):
        name = "test-hoge"
        nickname = name

        client = Client(schema)
        mutation = create_user_mutation(name, nickname)
        executed = client.execute(mutation)

        self.assertEqual(executed, {
            'data': {
                'createUser': {
                    'user': {
                        'name': name,
                        'nickname': nickname,
                        'avator': None,
                    }
                }
            }
        })

    def test_create_user_without_avator(self):
        name = "test-fuga"
        nickname = name
        avator = None

        client = Client(schema)
        mutation = create_user_mutation(name, nickname, avator)
        executed = client.execute(mutation)

        self.assertEqual(executed, {
            'data': {
                'createUser': {
                    'user': {
                        'name': name,
                        'nickname': nickname,
                        'avator': avator,
                    }
                }
            }
        })
