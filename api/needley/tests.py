from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

from .models import User, Article
from .schema import schema, UserNode

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


def post_article_mutation(user_id, title, content):
    return f'''
        mutation {{
            postArticle(input: {{
                userId:"{user_id}",
                articleTitle:"{title}",
                articleContent:"{content}",
            }}) {{
                article {{
                    title
                    content
                }}
            }}
        }}
        '''


class CreateUserTests(TestCase):
    def test_post_article(self):
        user = User.objects.create(name="hoge", nickname="hoge")
        user_id = to_global_id(UserNode._meta.name, user.pk)

        title = "fuga"
        content = "fuga fuga content"

        client = Client(schema)
        mutation = post_article_mutation(user_id, title, content)
        executed = client.execute(mutation)

        self.assertEqual(executed, {
            'data': {
                'postArticle': {
                    'article': {
                        'title': title,
                        'content': content,
                    }
                }
            }
        })
