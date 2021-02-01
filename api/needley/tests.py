from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

from .models import User, Article
from .schema import schema, UserNode


def create_user_mutation(name, email, password, nickname, avator=None):
    mutation = f'''
        mutation {{
            createUser(input: {{
                userName:"{name}"
                userEmail:"{email}"
                userPassword:"{password}"
                userNickname:"{nickname}"
                { 'userAvator:"' + avator + '"' if avator else "" }
            }}) {{
                user {{
                    username
                    profile {{
                        nickname
                        avator
                    }}
                }}
            }}
        }}
        '''

    expect = {
        'data': {
            'createUser': {
                'user': {
                    'username': name,
                    'profile': {
                        'nickname': nickname,
                        'avator': avator,
                    }
                }
            }
        }
    }

    return {
        'mutation': mutation,
        'expect': expect
    }

fake_name1 = "hoge-test"
fake_name2 = "fuga-test"
fake_email1 = "test1@example.com"
fake_email2 = "test2@example.com"
fake_password = "HogePass-01"
fake_avator_url = "https://example.com/icon.png"


class CreateUserTests(TestCase):
    def test_create_user(self):
        self.maxDiff = None
        name = fake_name1
        email = fake_email1
        password = fake_password
        nickname = name
        avator = fake_avator_url

        client = Client(schema)
        data = create_user_mutation(
            name, email, password, nickname, avator=avator)
        mutation = data['mutation']
        expect = data['expect']

        executed = client.execute(mutation)

        self.assertEqual(executed, expect)

    def test_create_user_without_avator(self):
        name = fake_name2
        email = fake_email2
        password = fake_password
        nickname = name
        avator = None

        client = Client(schema)
        data = create_user_mutation(
            name, email, password, nickname, avator=avator)
        mutation = data['mutation']
        expect = data['expect']

        executed = client.execute(mutation)

        self.assertEqual(executed, expect)


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


class PostArticleTests(TestCase):
    def test_post_article(self):
        user = User.objects.create(
            username=fake_name1, email=fake_email1, password=fake_password)
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
