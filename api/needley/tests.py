import json
from dataclasses import dataclass

from django.test import Client, TestCase
from graphene.test import Client as GraphQLClient
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

@dataclass
class UserData:
    username: str
    email: str
    password: str
    nickname: str = "hoge-nick"
    avator: str = None
    idx = 0

def get_mock_user(data_only=False):
    username = "test" + str(UserData.idx)
    email = username + "@example.com"
    password = "password"
    nickname = username + " (nick)"
    UserData.idx += 1

    if data_only:
        return UserData(username=username, email=email, password=password)
    else:
        return User.objects.create_user(username=username, email=email, password=password)

def post_query(query, login_as=None):
    client = Client()
    if login_as is True:
        user = get_mock_user()
        client.force_login(user)
    elif login_as:
        client.force_login(login_as)

    response = client.post('/graphql', {'query': query})
    parsed = json.loads(response.content)
    return parsed


class CreateUserTests(TestCase):
    def test_create_user(self):
        u = get_mock_user(data_only=True)

        data = create_user_mutation(
            u.username, u.email, u.password, u.nickname, avator=u.avator)
        mutation = data['mutation']
        expect = data['expect']
        result = post_query(mutation)

        self.assertEqual(result, expect)

    def test_create_user_without_avator(self):
        u = get_mock_user(data_only=True)

        data = create_user_mutation(
            u.username, u.email, u.password, u.nickname, avator=None)
        mutation = data['mutation']
        expect = data['expect']
        result = post_query(mutation)

        self.assertEqual(result, expect)


def post_article_mutation(user_id, title, content):
    mutation = f'''
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
    expect = {
        'data': {
            'postArticle': {
                'article': {
                    'title': title,
                    'content': content,
                }
            }
        }
    }

    return {
        'mutation': mutation,
        'expect': expect
    }




class PostArticleTests(TestCase):
    def test_post_article(self):
        user = get_mock_user()
        user_id = to_global_id(UserNode._meta.name, user.pk)

        title = "fuga"
        content = "fuga fuga content"
        data = post_article_mutation(user_id, title, content)
        mutation = data['mutation']
        expect = data['expect']

        result = post_query(mutation, login_as=True)

        self.assertEqual(result, expect)
